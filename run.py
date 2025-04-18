from app import create_app

# Create the Flask app using factory pattern
app = create_app()

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
