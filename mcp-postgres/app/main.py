from fastapi import FastAPI, HTTPException, Depends, status
import psycopg2
from psycopg2.extras import RealDictCursor
from .schemas import InsertCredentialsRequest
from .config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

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