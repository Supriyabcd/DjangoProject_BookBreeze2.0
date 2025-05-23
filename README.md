# Personalized E-Book Management System

## Overview
The Personalized E-Book Management System is a web-based application developed from August 2024 to December 2024 under the guidance of Prof. Amrita Chaturvedi. This project aims to provide a user-friendly platform for managing e-books, enabling users to browse, search, rate, review, and organize books into custom shelves. Additionally, it includes social features for connecting with friends, sharing book activity, and engaging in direct chats.

## Features
- **Book Browsing and Search**: Browse books by genre or search by title or author.
- **Book Management**: View detailed book information, including descriptions and metadata.
- **User Interaction**: Rate and review books, organize them into custom shelves, and track reading progress.
- **Social Features**: Connect with friends, share book activity, and communicate via direct chats.
- **Responsive Design**: User-friendly interface for seamless interaction across devices.

## Technical Tools
- **Backend**: Django (Python web framework)
- **Database**: SQLite
- **Version Control**: Git
- **Environment**: UNIX
- **IDE**: Visual Studio Code

## Installation
To set up the project locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/personalized-ebook-management-system.git
   cd personalized-ebook-management-system
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Database Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```
   The application will be available at `http://localhost:8000`.

## Usage
- **Browsing Books**: Navigate to the books section to browse by genre or use the search bar to find books by title or author.
- **Managing Books**: Add books to custom shelves, rate them, and write reviews from the book details page.
- **Tracking Progress**: Update your reading progress for each book.
- **Social Features**: Connect with friends, view their book activity, and start direct chats from the social dashboard.

## Project Structure
```
book_comparison/
├── book_comparison/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── book_covers/
├── main/
│   ├── __pycache__/
│   ├── management/
│   │   ├── commands/
│   │   │   ├── populate_shelves.py
│   │   │   ├── populate_user_profiles.py
│   ├── migrations/
│   ├── templates/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
├── media/
│   ├── book_covers/
├── static/
├── db.sqlite3
├── manage.py
├── README.md
```

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.
