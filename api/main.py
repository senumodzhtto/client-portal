import os, time, sqlite3
from fastapi import FastAPI, HTTPException, Depends, Request
from passlib.context import CryptContext
import jwt

PORTAL_DB="/opt/portal/portal.db"
XUI_DB="/etc/x-ui/x-ui.db"
JWT_SECRET="NL27Z4a4HzjKKy-3MbxPjWKe7saWE9OkWPT4HF0v7zmsZW1Da_R815vZAHnLkjc"

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()

def portal_db():
    conn = sqlite3.connect(PORTAL_DB)
    conn.row_factory = sqlite3.Row
    return conn

def xui_db():
    conn = sqlite3.connect(XUI_DB)
    conn.row_factory = sqlite3.Row
    return conn

def make_token(email):
    now=int(time.time())
    payload={"sub":email,"iat":now,"exp":now+604800}
    return jwt.encode(payload,JWT_SECRET,algorithm="HS256")

def get_user(req:Request):
    auth=req.headers.get("authorization","")
    if not auth.startswith("Bearer "):
        raise HTTPException(401,"No token")
    token=auth.split(" ")[1]
    try:
        data=jwt.decode(token,JWT_SECRET,algorithms=["HS256"])
        return data["sub"]
    except:
        raise HTTPException(401,"Invalid token")

@app.post("/auth/login")
async def login(data:dict):
    email=data["email"]
    password=data["password"]

    conn=portal_db()
    user=conn.execute("SELECT * FROM portal_users WHERE email=?",(email,)).fetchone()
    conn.close()

    if not user:
        raise HTTPException(401,"Invalid login")

    if not pwd_ctx.verify(password,user["password_hash"]):
        raise HTTPException(401,"Invalid login")

    return {"token":make_token(email)}

@app.get("/me/usage")
async def usage(email:str=Depends(get_user)):

    conn=xui_db()

    row=conn.execute("""
    SELECT
    SUM(up) as up,
    SUM(down) as down,
    SUM(total) as quota,
    MAX(expiry_time) as expiry,
    MAX(last_online) as last
    FROM client_traffics
    WHERE email=?
    """,(email,)).fetchone()

    conn.close()

    up=row["up"] or 0
    down=row["down"] or 0
    used=up+down
    quota=row["quota"] or 0

    return {
        "upload":up,
        "download":down,
        "used":used,
        "quota":quota,
        "remaining":None if quota==0 else quota-used,
        "expiry":row["expiry"],
        "last_online":row["last"]
    }
