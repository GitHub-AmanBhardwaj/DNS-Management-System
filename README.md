# DNS Management System

A Flask-based web application for managing DNS records, featuring a modern, dark-themed, and responsive user interface. It enables users to create, edit, and delete DNS records (A, CNAME, MX, TXT) with a SQLite database for persistent storage and a RESTful API for programmatic access. The system includes simulated DNS updates, designed for easy integration with real DNS servers.

## Features
- **DNS Record Management**: Create, edit, and delete A, CNAME, MX, and TXT records with robust input validation.
- **SQLite Database**: Stores records in a lightweight, persistent database for reliable data management.
- **Simulated DNS Updates**: Provides a placeholder function for DNS updates, configurable for real DNS server integration.
- **Sleek UI**: Dark-themed, responsive interface with smooth animations, powered by Google Fonts and Material Icons.
- **RESTful API**: Supports programmatic operations for listing, creating, updating, and deleting records.
- **User Feedback**: Displays animated flash messages for success and error notifications.
- **Mobile-Optimized**: Features a collapsible navigation menu and adaptive layout for seamless mobile use.

## Prerequisites
- Python 3.6 or higher
- Flask (`pip install flask`)
- dnspython (`pip install dnspython`)
- SQLite (included with Python)

## Installation
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd dns-management-system
   ```
2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install flask dnspython
   ```
4. **Run the Application**:
   ```bash
   python app.py
   ```
   The app will be available at `http://127.0.0.1:5000` in debug mode.

## Usage
### Web Interface
- **Home**: View all DNS records for the configured domain in a stylish table with options to edit or delete.
- **Add Record**: Access a form to create a new DNS record, with fields for name, type, value, and TTL.
- **Edit Record**: Modify an existing record using a pre-filled form.
- **Delete Record**: Remove a record with a confirmation prompt via a delete button.
- **Feedback**: Success or error messages appear as animated alerts after actions.

### API Endpoints
The RESTful API enables programmatic DNS record management:
- **List Records**:
  - `GET /api/records?domain=<domain>`: Fetch all records for a specified domain.
  - Example: `curl http://127.0.0.1:5000/api/records`
- **Create Record**:
  - `POST /api/records`: Create a new record.
  - Body: `{"domain": "example.com", "name": "www", "type": "A", "value": "192.168.1.1", "ttl": 300}`
  - Example: `curl -X POST -H "Content-Type: application/json" -d '{"name":"www","type":"A","value":"192.168.1.1"}' http://127.0.0.1:5000/api/records`
- **Update Record**:
  - `PUT /api/records/<id>`: Update an existing record.
  - Body: `{"name": "www", "type": "A", "value": "192.168.1.2", "ttl": 600}`
  - Example: `curl -X PUT -H "Content-Type: application/json" -d '{"name":"www","type":"A","value":"192.168.1.2"}' http://127.0.0.1:5000/api/records/1`
- **Delete Record**:
  - `DELETE /api/records/<id>`: Delete a record by ID.
  - Example: `curl -X DELETE http://127.0.0.1:5000/api/records/1`

## Project Structure
Below is a pattern-based chart representing the project structure:

```
dns-management-system/
│
├── app.py                    # Core Flask app with routes, database logic, and DNS simulation
├── dns_records.db            # SQLite database (auto-generated on first run)
│
└── templates/                # HTML templates for the web interface
    ├── layout.html           # Base template with navigation and global styles
    ├── index.html            # Displays DNS record list with table and empty state
    ├── add.html              # Form for adding new DNS records
    └── edit.html             # Form for editing existing DNS records
```

## Configuration
Customize the application by editing `app.py`:
- **DNS_SERVER**: DNS server IP (default: `127.0.0.1`).
- **DOMAIN**: Default domain (default: `aman@cloud`).
- **KEYRING**: TSIG keyring for secure DNS updates (default: `None`).
- **Secret Key**: Flask secret key set to `"supersecretkey"`. Replace with a secure value for production.
