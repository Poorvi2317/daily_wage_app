from app import app  # Import the Flask app instance from the app module

if __name__ == "__main__":  # Ensure this file runs only when executed directly, not when imported
    app.run(debug=True)  # Start the Flask development server with debug mode enabled
