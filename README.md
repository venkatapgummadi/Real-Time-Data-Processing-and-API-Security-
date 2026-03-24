# Project 3: Real-Time Data Processing and API Security Framework

This project implements a secure, real-time transaction processing system using FastAPI, OAuth2, and JWT.

## How to Test This Project

### 1. Install Dependencies
Ensure you have the required packages installed:
```bash
pip install -r requirements.txt
```

### 2. Run the Server
Start the FastAPI server using `uvicorn`:
```bash
python -m uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### 3. Test with Swagger UI (Easiest)
1. Open your browser and go to `http://127.0.0.1:8000/docs`.
2. Click the **Authorize** button and enter:
   - **Username:** `admin`
   - **Password:** `admin123`
3. Now all protected routes are accessible!
4. Try the `POST /transactions` endpoint with a sample JSON:
   ```json
   {
     "user_id": "user_001",
     "amount": 150.50,
     "currency": "USD",
     "description": "Payment for services"
   }
   ```

### 4. Test with curl (Command Line)
**Step 1: Get Token**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin&password=admin123'
```

**Step 2: Submit Transaction (Using the token from Step 1)**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/transactions' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": "user_001",
  "amount": 100,
  "currency": "USD"
}'
```

