const session = require('express-session');
const express = require('express');
const bcrypt = require('bcrypt');
const { findUserByUsername } = require('./path/to/your/userModel'); // Adjust the import as necessary

const app = express();

app.use(session({
    secret: 'melomood.com', // Change this to a more secure, randomly generated secret in production
    resave: false,
    saveUninitialized: true,
    cookie: {
        maxAge: 1000 * 60 * 60, // 1 hour
        secure: false, // Set to true if using HTTPS
        httpOnly: true // Helps mitigate XSS attacks
    }
}));

app.post('/login', async (req, res) => {
    const { username, password } = req.body;

    try {
        const user = await findUserByUsername(username);

        if (user && await bcrypt.compare(password, user.password_hash)) {
            req.session.userId = user.id;  // Save user ID in session
            res.redirect('/dashboard');
        } else {
            res.status(401).send('Invalid credentials. Please try again.'); // Better status code
        }
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).send('Internal Server Error');
    }
});

app.get('/dashboard', (req, res) => {
    if (req.session.userId) {
        res.send('Welcome to the dashboard!');
    } else {
        res.redirect('/login');
    }
});

// Logout route
app.post('/logout', (req, res) => {
    req.session.destroy(err => {
        if (err) {
            console.error('Error during logout:', err);
            return res.status(500).send('Could not log out');
        }
        res.redirect('/login');
    });
});
