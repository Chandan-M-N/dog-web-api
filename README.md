# Dog Breed Explorer 🐕

A Flask web application for managing dog breeds and sub-breeds with PostgreSQL database integration.

## Features

- Browse dog breeds and sub-breeds
- Add new breeds and sub-breeds
- Edit existing entries
- Delete breeds or specific sub-breeds
- Responsive design

## Prerequisites

- Docker
- Python 3.11+
- PostgreSQL database (local or remote)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Chandan-M-N/dog-web-api.git
cd dog-web-api
```

### 2. Build the Docker Image

```bash
docker build -t dogwebapi .
```

### 3. Run the Application

#### Option A: Using individual environment variables
```bash
docker run -d -p 5100:5100 \
  -e DB_NAME='your_db_name' \
  -e DB_USER='your_db_user' \
  -e DB_PASSWORD='your_db_password' \
  -e DB_HOST='your_db_host' \
  -e DB_PORT='your_db_port' \
  -e FLASK_SECRET_KEY='your_secret_key' \
  dogwebapi
```

### 4. Access the Application

Open your browser and visit:  
[http://localhost:5100](http://localhost:5100)

## Development

### Without Docker

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add Database Configuration to .env and uncomment load_dotenv() in /models/db.py

4. Run the application:
   ```bash
   python3 app.py
   ```

## Project Structure

```
dog-breed-explorer/
├── app.py                # Main application file
├── models/
│   └── db.py            # Database operations
├── static/
│   └── dogs.css/             # CSS files
|   └── index.css/
├── templates/   
|   └── dogs.html/
|   └── index.html/        # HTML templates
├── Dockerfile           # Docker configuration
├── requirements.txt     # Python dependencies
├── dogs.json            # Data for some breeds and sub breeds
├── LICENSE.md           # Apache 2.0 License
└── README.md            # This file

```

## License

Apache 2.0 License