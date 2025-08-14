# E-Commerce Web Application

## Overview

This project is a full-stack e-commerce web application built using **React.js** for the frontend and **Django** for the backend. Users can browse products, add them to their cart, checkout with payment options, and receive order confirmation emails with invoice links.

---

## Features

* **User Authentication**: Login, Register, Logout.
* **Product Catalog**: Products categorized into:

  * Mobile & Accessories
  * Computers & Laptops
  * Audio & Headphones
  * Smart Home & Wearables
  * Gaming & Entertainment
* **Cart Management**: Add, view, and remove products from cart.
* **Checkout**: Cash on Delivery or Credit Card payment options.
* **Order Confirmation**: Sends email with invoice link after successful order.
* **Responsive UI**: Clean, premium look for all devices.

---

## Tech Stack

* **Frontend**: React.js, HTML5, CSS3, JavaScript
* **Backend**: Django, Django REST Framework
* **Database**: SQLite (default, can be replaced with PostgreSQL)
* **Email**: SMTP (for order confirmation emails)
* **Authentication**: Token-based authentication

---

## Installation

### Backend

1. Clone the repository:

```bash
git clone <repository_url>
cd <backend_folder>
```

2. Create a virtual environment:

```bash
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (for admin):

```bash
python manage.py createsuperuser
```

6. Run the server:

```bash
python manage.py runserver
```

### Frontend

1. Navigate to frontend folder:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Run the development server:

```bash
npm start
```

---

## Usage

1. Open the application at `http://localhost:3000`.
2. Register or login.
3. Browse products and add to cart.
4. Checkout and place your order.
5. Receive confirmation email with invoice link.

---

## Folder Structure

```
├── backend/
│   ├── manage.py
│   ├── api/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProductCard.js
│   │   │   ├── Navbar.js
│   │   │   └── ...
│   │   ├── pages/
│   │   │   ├── ProductsPage.js
│   │   │   ├── Cart.js
│   │   │   └── Checkout.js
│   │   └── App.js
│   └── package.json
├── README.md
└── requirements.txt
```

---

## API Endpoints

| Endpoint                 | Method | Description              |
| ------------------------ | ------ | ------------------------ |
| `/api/products/`         | GET    | Fetch all products       |
| `/api/cart/`             | GET    | Get current user’s cart  |
| `/api/cart/add/`         | POST   | Add product to cart      |
| `/api/cart/remove/<id>/` | DELETE | Remove product from cart |
| `/api/place-order/`      | POST   | Place an order           |

---

## Contributing

1. Fork the repository.
2. Create a branch: `git checkout -b feature-name`.
3. Commit changes: `git commit -m "Add feature"`.
4. Push branch: `git push origin feature-name`.
5. Create a pull request.

---

## License

This project is licensed under the MIT License.
