
Project Setup & Run Instructions
1. Prerequisites

Before running the project, ensure you have:

Docker and Docker Compose installed

Python 3.11+ (if running locally without Docker)

Git (to clone the repository)

Check Docker:

docker --version
docker-compose --version

2. Clone the Repository
git clone https://github.com/Hari7467/Interview.git
cd Interview/backend-engineer

3. Directory Structure

The project contains:

backend-engineer/
├─ user_service/
├─ product_service/
├─ order_service/
├─ notification_service/
├─ gateway/
├─ docker-compose.yml
├─ README.md

4. Environment Variables

Each service has its own .env file. For example:

gateway/.env

USER_SERVICE_URL=http://user_service:8001
PRODUCT_SERVICE_URL=http://product_service:8002
ORDER_SERVICE_URL=http://order_service:8003
SECRET_KEY=mysecret


user_service/.env, product_service/.env, order_service/.env contain DB and Redis settings.

Make sure all .env files are correctly set before starting the services.

5. Build & Start Services with Docker Compose

From the project root:

# Build all services
docker-compose build

# Start services in detached mode
docker-compose up -d


This will start:

Redis (6379)

Postgres for each service (5433, 5434, 5435)

User, Product, Order, Notification services

API Gateway (8000)

6. Check Service Status
docker-compose ps


You should see all containers running.

7. API Gateway

All requests go through the Gateway:

http://localhost:8000

7.1 Users Service
Endpoint	Method	Body / Headers
/users/register	POST	JSON: {"email":"", "password":"", "full_name":""}
/users/login	POST	JSON: {"email":"", "password":""}
/users/me	GET	Header: x-user-id: <JWT token>
7.2 Products Service
Endpoint	Method	Body / Params
/products	GET	None
/products	POST	JSON: {"sku":"", "name":"", "description":"", "price":0, "quantity":0}
/products/{product_id}	GET	Path param: product_id
/products/{product_id}	PUT	JSON: same as POST
/products/{product_id}	DELETE	Path param: product_id
/products/{product_id}/adjust-stock	POST	Path param + JSON if needed
7.3 Orders Service
Endpoint	Method	Body / Params
/orders	GET	None
/orders	POST	JSON: {"user_id":1, "product_id":1, "quantity":1}
/orders/{order_id}	GET	Path param: order_id
/orders/{order_id}	PATCH	Path param + JSON if needed
/orders/{order_id}/pay	POST	Path param: order_id
8. Swagger UI

All APIs are documented via FastAPI Swagger UI:

http://localhost:8000/docs


You can test endpoints here.

Make sure to provide body JSON and JWT headers for endpoints like /users/me.

9. Stop Services
docker-compose down

10. Optional: Running Locally Without Docker

Activate your Python environment:

python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows


Install requirements:

pip install -r requirements.txt


Start each service individually:

uvicorn user_service.main:app --host 0.0.0.0 --port 8001 --reload
uvicorn product_service.main:app --host 0.0.0.0 --port 8002 --reload
uvicorn order_service.main:app --host 0.0.0.0 --port 8003 --reload
uvicorn gateway.main:app --host 0.0.0.0 --port 8000 --reload

11. Testing JWT Token

Register a user via /users/register.

Login via /users/login to get JWT token in response.

Use the JWT token in headers for protected endpoints:

x-user-id: <JWT token>
