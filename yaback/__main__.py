from src.app import app
import os

if __name__ == '__main__':
    app.run(debug=True,
            host=os.environ.get("HOST", ""),
            port=os.environ.get("PORT", ""),
            threaded=True)