# GymApp - Gym Management System

A comprehensive Windows desktop application for managing gym members, tracking membership expirations, and monitoring payments.

## Features

- **Member Management**: Add, edit, and manage gym member information
- **Membership Tracking**: Automatic tracking of membership expiration dates
- **Payment Management**: Record and track member payments
- **Persian Calendar Support**: Integrated Jalali (Persian) calendar support using jdatetime
- **User Authentication**: Secure login system for gym staff
- **Modern UI**: Clean and intuitive interface built with PyQt5

## Screenshots
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/c04a0df3-21f5-419b-9f22-6b1c48176614" />
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/c2a31189-72b0-4213-9f22-2d2731fea4e2" />
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/23d98a2c-a37e-48c5-8fdc-275f79e5f27c" />
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/ea052a73-b198-46ee-90e0-bd7d5b581f6d" />
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/65824a03-9997-4e91-9b75-86555de013cb" />


## Technology Stack

- **Python**: 3.13.3
- **GUI Framework**: PyQt5
- **Database**: SQLite (via custom database module)
- **Calendar**: jdatetime (Persian/Jalali calendar support)

## Installation

### Prerequisites

- Windows Operating System
- Python 3.13.3 or higher

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/GymApp.git
cd GymApp
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python App.py
```

## Requirements

```
PyQt5>=5.15.0
jdatetime>=4.1.0
```

## Project Structure

```
GymApp/
├── Dir/                    # Source code directory
│   ├── 
│   ├── LoginWidget.py     # Login interface
│   ├── MembersWidget.py   # Members management interface
│   ├── ManageWidget.py    # Management interface
│   ├── SettingWidget.py   # Settings interface
│   └── database.py        # Database operations
├──  App.py                # Main application entry point
├── .gitignore
├── README.md
└── requirements.txt
```

## Building Executable

To create a standalone executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed Dir/App.py
```

The executable will be created in the `dist/` folder.

## Usage

1. **Login**: Start the application and log in with your credentials
2. **Add Members**: Navigate to the Members section to add new gym members
3. **Track Expiration**: View and manage membership expiration dates
4. **Record Payments**: Track and manage member payment history
5. **Settings**: Configure application settings as needed

## Database

The application uses SQLite database to store:
- Member information
- Membership expiration dates
- Payment records
- User authentication data

## Development

### Setting up Development Environment

1. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Your Name**
- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)

## Acknowledgments

- PyQt5 for the GUI framework
- jdatetime for Persian calendar support

## Support

For support, please open an issue in the GitHub repository or contact [your.email@example.com]

## Roadmap

- [ ] Add reporting features
- [ ] Implement backup and restore functionality
- [ ] Add email/SMS notifications for expiring memberships
- [ ] Multi-language support
- [ ] Cloud backup integration

---

**Note**: This application is designed for Windows desktop environments.
