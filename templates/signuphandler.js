const express = require('express');
const bcrypt = require('bcrypt');
const { saveUser } = require('./path/to/your/userModel'); // Adjust the import as necessary
const { body, validationResult } = require('express-validator');

const app = express();
app.use(express.json()); // To parse JSON body

app.post('/signup', 
    // Validate input
    body('username').notEmpty().withMessage('Username is required'),
    body('email').isEmail().withMessage('Valid email is required'),
    body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters long'),
    async (req, res) => {
        // Check for validation errors
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() });
        }

        const { username, password, email } = req.body;
        try {
            const hashedPassword = await bcrypt.hash(password, 10);  // Hash password

            // Save the user to the database
            await saveUser({ username, email, password_hash: hashedPassword });
            
            // Redirect to login page after successful signup
            return res.redirect('/login'); // Redirecting to the login page
        } catch (error) {
            console.error('Error saving user:', error);
            // Return a JSON response with an error message
            return res.status(500).json({ message: 'Internal Server Error' });
        }
    }
);

// Example route for login
app.get('/login', (req, res) => {
    // Render your login page or return a message
    res.send('Login Page'); // Replace with your actual login page rendering logic
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
