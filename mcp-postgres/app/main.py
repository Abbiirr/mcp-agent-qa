from fastapi import FastAPI, HTTPException, Depends, status, Request
import psycopg2
from psycopg2.extras import RealDictCursor
from .schemas import InsertCredentialsRequest
from .config import settings
import logging
from fastapi.responses import JSONResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def get_db_connection():
    """Get a database connection with schema set correctly"""
    conn = psycopg2.connect(settings.DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SET search_path TO %s", (settings.DB_SCHEMA_NAME,))
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        conn.close()
        raise HTTPException(status_code=500, detail="Database connection failed")

def get_conn():
    try:
        conn = psycopg2.connect(settings.DATABASE_URL, cursor_factory=RealDictCursor)
        try:
            # Set schema if needed
            with conn.cursor() as cursor:
                cursor.execute("SET search_path TO %s", (settings.DB_SCHEMA_NAME,))
            yield conn
        finally:
            conn.close()
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@app.post("/insert_user", status_code=status.HTTP_201_CREATED)
def insert_credentials(req: InsertCredentialsRequest, conn=Depends(get_conn)):
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO user_login_credentials
              (user_id, first_name, last_name, email, phone_number, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                req.user_id,
                req.first_name,
                req.last_name,
                req.email,
                req.phone_number,
                req.is_active,
            ),
        )
        new_id = cur.fetchone()["id"]
        conn.commit()
        return {"inserted_id": new_id}
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    rpc = await request.json()
    # Basic JSON-RPC 2.0 validation
    if rpc.get("jsonrpc") != "2.0" or "method" not in rpc or "params" not in rpc or "id" not in rpc:
        raise HTTPException(400, "Invalid JSON-RPC 2.0 envelope")
    method, params, req_id = rpc["method"], rpc["params"], rpc["id"]

    if method == "insert_credentials":
        # Validate params
        try:
            body = InsertCredentialsRequest(**params)
        except Exception as ve:
            return JSONResponse(
                status_code=400,
                content={"jsonrpc":"2.0","id":req_id,
                         "error":{"code":-32602,"message":"Invalid params","data":str(ve)}}
            )
        # Perform DB insertion
        conn = None
        try:
            conn = get_db_connection()  # Use the direct function instead
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO user_login_credentials
                  (user_id, first_name, last_name, email, phone_number, is_active)
                VALUES (%s,%s,%s,%s,%s,%s)
                RETURNING id
                """,
                (body.user_id, body.first_name, body.last_name,
                 body.email, body.phone_number, body.is_active),
            )
            inserted = cur.fetchone()["id"]
            conn.commit()
            result = {"inserted_id": inserted}
        except Exception as e:
            if conn:
                conn.rollback()
            return JSONResponse(
                status_code=500,
                content={"jsonrpc":"2.0","id":req_id,
                         "error":{"code":-32000,"message":"DB error","data":str(e)}}
            )
        finally:
            if conn:
                conn.close()
        return {"jsonrpc":"2.0","id":req_id,"result":result}