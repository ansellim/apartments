from app import app
import os
if __name__ == "__main__":
    port = os.environ.get("PORT",5000)
    app.run(debug=False, port=port)
