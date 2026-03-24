from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import asyncio
from security.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    oauth2_scheme
)
from transactions.schema import Transaction
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Async Queue for transactions
transaction_queue = asyncio.Queue()

app = FastAPI(
    title="Real-Time Security Framework",
    description="Mock Financial / Payment Gateway Style API",
    version="1.0.0"
)

# Add rate limit exceeded handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

async def process_transactions_worker():
    """
    Background worker that processes transactions from the queue.
    (Real-world replacement: SQS / RabbitMQ)
    """
    while True:
        # Get a transaction from the queue
        transaction = await transaction_queue.get()
        print(f"[WORKER] Processing transaction {transaction.transaction_id} for user {transaction.user_id}...")
        
        # Simulate processing time
        await asyncio.sleep(2) 
        
        # Mock Decision
        decision = "APPROVED" if transaction.amount < 1000 else "FLAGGED"
        print(f"[WORKER] Decision for {transaction.transaction_id}: {decision}")
        
        # Finish task
        transaction_queue.task_done()

@app.on_event("startup")
async def startup_event():
    # Start the background worker
    asyncio.create_task(process_transactions_worker())

# IP Blacklist (Add specific IPs here to block them)
BANNED_IPS = {"1.1.1.1", "2.2.2.2"}  # Dummy example IPs

@app.middleware("http")
async def block_banned_ips(request: Request, call_next):
    """
    Middleware to intercept requests and block any IP address present in the BANNED_IPS set.
    """
    client_ip = request.client.host
    if client_ip in BANNED_IPS:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=403, 
            content={"detail": f"Access denied. IP {client_ip} is blacklisted."}
        )
    return await call_next(request)

# Mocked user database (in production, use a real DB)
MOCK_USER_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("admin123"), # Default password
        "disabled": False,
    }
}

@app.get("/health")
async def health_check():
    return {"status": "secure"}

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates a user and returns a JWT access token.
    """
    user = MOCK_USER_DB.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    """
    A protected endpoint that returns the current user's identity.
    """
    return {"username": "admin", "token": token}

@app.post("/transactions")
@limiter.limit("5/minute")
async def submit_transaction(request: Request, transaction: Transaction, token: str = Depends(oauth2_scheme)):
    """
    Accepts a transaction payload and puts it into the processing queue.
    """
    # Assign a temp ID if not provided
    if not transaction.transaction_id:
        transaction.transaction_id = "TXN-" + transaction.user_id[:3].upper() + "-TEMP"

    # Add to queue for background processing
    await transaction_queue.put(transaction)
    print(f"[API] Queued transaction {transaction.transaction_id} for user: {transaction.user_id}")
    
    return {
        "status": "queued",
        "message": "Transaction received and queued for background processing",
        "transaction_id": transaction.transaction_id,
        "processed_by": "async-worker"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
