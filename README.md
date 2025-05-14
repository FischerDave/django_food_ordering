# Django_food_ordering

This project provides a RESTful API for managing restaurants, menu items, and customer orders. It includes user authentication, restaurant listings with menus, order creation, and order status updates.

## Documentation Compliance

This project adheres to the following documentation standards:

* Code Comments: All code is thoroughly commented in English, explaining the purpose and functionality of different sections, classes, methods, and important logic.
* README File: This README.md file provides a comprehensive overview of the project, including setup instructions, running tests, and starting the application.
* Clear Naming Conventions: Variables, functions, and classes are named descriptively to enhance readability and understanding.
* Serializer Documentation: Serializers clearly document the data transformation and validation processes for API requests and responses.
* View Documentation: Views are documented to explain their purpose, the HTTP methods they handle, the permissions required, and the expected request and response formats.
* Model Documentation: Models include docstrings explaining their purpose and the meaning of each field.
* URL Configuration Documentation: The urls.py file is documented to explain the mapping of URL patterns to their corresponding views.
* Test Documentation: Test cases in tests.py are documented to describe the functionality being tested and the expected outcomes.

## Local Setup Instructions

Follow these steps to set up the project locally using a virtual environment:

### 1. Install Python 3.12

Ensure you have Python 3.12 installed on your system. You can download it from the official Python website: https://www.python.org/downloads/

### 2. Create and Activate Virtual Environment

Open your terminal or command prompt, navigate to the project directory, and create a virtual environment using the following command:
```bash
python -m venv .venv
```
Activate the virtual environment:

* On macOS and Linux:
```source .venv/bin/activate```
* On Windows:
```.venv\Scripts\activate```

### 3. Install Dependencies

Install the required Python packages from the requirements.txt file (you might need to create this file based on your project's dependencies, including Django and Django REST Framework) using the following command:

```bash
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
```
(Example requirements.txt content):

Django>=4.0
djangorestframework>=3.13
djangorestframework-simplejwt>=4.8
django-environ>=0.9

### 4. Database Initialization (Using SQLite - Embedded Database)

This project is configured to use SQLite by default, which is a simple file-based database and doesn't require a separate server. Here's how to initialize it:

1.  **Ensure `sqlite3` is installed:** Python usually comes with `sqlite3` built-in.

2.  **Apply Migrations:** Run the migrate command to create the database file (`db.sqlite3`) and the necessary tables:

	```bash
	python manage.py migrate
	```

	This command will automatically create the `db.sqlite3` file in your project's root directory if it doesn't exist.

3.  **Create a Superuser (for admin access):**

	```bash
	python manage.py createsuperuser
	```

	Follow the prompts to enter a username, email address, and password.

4.  **Populating the Database with Sample Data (Optional):**

	If you have created the `populate_db.py` management command (as described in a previous response), you can run it to populate your database with initial data, including a test user (`username="testcustomer"`, `password="$ecret123"`), a sample restaurant, and menu items. To execute this command, run the following in your terminal:

	```bash
	python manage.py populate_db
	```

5.  **Clearing the Database (Optional):**

	If you have created a `clear_db.py` management command, you can use it to reset the database to an empty state after migrations. This is useful for development or testing. To execute this command, run the following in your terminal:

	```bash
	python manage.py clear_db
	```

	**Note:** If you don't have a `clear_db.py` command, you can manually delete the `db.sqlite3` file, but this will *completely* erase all data, including the superuser. Re-run `python manage.py migrate` after deleting the file.


### 5. Running Tests

To run the project's tests, execute the following command within the activated virtual environment:
```bash
python manage.py test
```
This command will discover and run all test cases defined in your project's tests.py files. Ensure all tests pass to verify the functionality of your API.

### 6. Starting the Project

To start the development server, run the following command within the activated virtual environment:

```python manage.py runserver```

This will start the Django development server, and you can access the API endpoints at http://127.0.0.1:8000/api/ (or the base URL you've configured).

### 5. Quick Start with Docker Compose

For a faster and more isolated setup, you can use Docker Compose. This method requires Docker and Docker Compose to be installed on your system.

To run the application using Docker, use Docker Compose:
```codebox
docker compose up --build
```
This command will build the Docker image and start the Django development server within a container. The API will be accessible at http://localhost:8000/api/

Once the application is running, you can access the API documentation at the following URLs:

-   **Swagger UI (Docs):** `http://localhost:8000/api/schema/swagger-ui/`

## API Endpoints

This section describes the available API endpoints. For interactive documentation and testing, please refer to the Swagger UI at `/api/schema/swagger-ui/` once the application is running.

### Authentication Endpoints

* **`POST /api/auth/register/`**: Registers a new user.
    * **Body Parameters (application/json):**
        * `username` (required): The desired username.
        * `password` (required): The user's password.
        * `email` (optional): The user's email address.
    * **Response (application/json):**
        * `token`: The authentication token for the newly registered user (HTTP 201 Created).
        * Error details (HTTP 400 Bad Request).

* **`POST /api/auth/login/`**: Logs in an existing user.
    * **Body Parameters (application/json):**
        * `username` (required): The user's username.
        * `password` (required): The user's password.
    * **Response (application/json):**
        * `token`: The authentication token for the logged-in user (HTTP 200 OK).
        * `error`: Error message for invalid credentials (HTTP 401 Unauthorized).
        * Error details (HTTP 400 Bad Request).

* **`GET /api/auth/who-am-i/`**: Retrieves information about the currently authenticated user.
    * **Headers:**
        * `Authorization`: `Token <your_authentication_token>` (required).
    * **Response (application/json):**
        * User details including `id`, `username`, `email` (HTTP 200 OK).
        * Authentication error (HTTP 401 Unauthorized).

### Restaurant Endpoints

* **`GET /api/restaurants/`**: Lists all available restaurants.
    * **Headers:**
        * `Authorization`: `Token <your_authentication_token>` (optional, but some implementations might require it).
    * **Response (application/json):**
        * A list of restaurant objects, each containing `id`, `name`, `address` (HTTP 200 OK).

* **`GET /api/restaurants/<int:pk>/`**: Retrieves details of a specific restaurant.
    * **Path Parameter:**
        * `pk`: The ID of the restaurant.
    * **Headers:**
        * `Authorization`: `Token <your_authentication_token>` (optional, but some implementations might require it).
    * **Response (application/json):**
        * Details of the requested restaurant (HTTP 200 OK).
        * Not Found error (HTTP 404 Not Found).

* **`GET /api/restaurants/<int:id>/menu/`**: Retrieves the menu of a specific restaurant.
    * **Path Parameter:**
        * `id`: The ID of the restaurant.
    * **Headers:**
        * `Authorization`: `Token <your_authentication_token>` (optional, but some implementations might require it).
    * **Response (application/json):**
        * A list of menu item objects, each containing `id`, `restaurant`, `name`, `price` (HTTP 200 OK).
        * Not Found error (HTTP 404 Not Found).

### Order Endpoints (Customer)

* **`POST /api/orders/`**: Creates a new order for the authenticated customer.
    * **Headers:**
        * `Authorization`: `Token <your_authentication_token>` (required).
    * **Body Parameters (application/json):**
        * `restaurantId` (required): The ID of the restaurant for the order.
        * `items` (required): An array of order items, where each item is an object with:
            * `menuItemId` (required): The ID of the menu item.
            * `quantity` (required): The quantity of the menu item.
    * **Response (application/json):**
        * Details of the newly created order (HTTP 201 Created).
        * Error details (HTTP 400 Bad Request).
        * Authentication error (HTTP 401 Unauthorized).

* **`GET /api/orders/<int:pk>/`**: Retrieves details of a specific order for the authenticated customer.
    * **Path Parameter:**
        * `pk`: The ID of the order.
    * **Headers:**
        * `Authorization`: `Token <your_authentication_token>` (required).
    * **Response (application/json):**
        * Details of the requested order, including items, customer information, and status (HTTP 200 OK).
        * Not Found error (HTTP 404 Not Found) if the order does not belong to the authenticated customer.
        * Authentication error (HTTP 401 Unauthorized).

### Order Endpoints (Restaurant - Assuming User-Restaurant Association)

* **`GET /api/restaurants/orders/`**: Lists all orders associated with the restaurant(s) managed by the authenticated user.
    * **Headers:**
        * `Authorization`: `Token <your_authentication_token>` (required).
    * **Response (application/json):**
        * A list of order objects (HTTP 200 OK).
        * Authentication error (HTTP 401 Unauthorized).

* **`GET /api/restaurants/orders/<int:pk>/`**: Retrieves details of a specific order associated with the restaurant(s) managed by the authenticated user.
    * **Path Parameter:**
        * `pk`: The ID of the order.
    * **Headers:**
        * `Authorization`: `Token <your_authentication_token>` (required).
    * **Response (application/json):**
        * Details of the requested order (HTTP 200 OK).
        * Not Found error (HTTP 404 Not Found) if the order is not associated with the user's restaurant(s).
        * Authentication error (HTTP 401 Unauthorized).

* **`PATCH /api/restaurants/orders/<int:pk>/update/`**: Updates the status of a specific order.
    * **Path Parameter:**
        * `pk`: The ID of the order.
    * **Headers:**
        * `Authorization`: `Token <your_authentication_token>` (required).
    * **Body Parameters (application/json):**
        * `status` (required): The new status of the order (e.g., "PROCESSING", "SHIPPED", "DELIVERED").
    * **Response (application/json):**
        * Details of the updated order (HTTP 200 OK).
        * Error details (HTTP 400 Bad Request).
        * Not Found error (HTTP 404 Not Found) if the order is not associated with the user's restaurant(s).
        * Authentication error (HTTP 401 Unauthorized).