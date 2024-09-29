const bcrypt = require('bcrypt');
const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const app = express();

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(session({
    secret: 'your_secret_key',
    resave: false,
    saveUninitialized: true,
}));

// Login Route
app.post('/login', async (req, res) => {
    const { username, password } = req.body;

    // Input validation
    if (!username || !password) {
        return res.status(400).send('Username and password are required.');
    }

    // Assume `findUserByUsername` retrieves user data from the database
    const user = await findUserByUsername(username);

    if (user) {
        // Compare entered password with the stored hashed password
        const match = await bcrypt.compare(password, user.password_hash);
        if (match) {
            req.session.userId = user.id;  // Save user ID in session
            return res.redirect('/dashboard');  // Redirect to dashboard on success
        } else {
            return res.status(401).send('Invalid credentials');  // Unauthorized
        }
    } else {
        return res.status(404).send('User not found');  // Not found
    }
});

// Additional routes can go here
app.get('/dashboard', (req, res) => {
    if (req.session.userId) {
        res.send('Welcome to the dashboard!');
    } else {
        res.redirect('/login');
    }
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
