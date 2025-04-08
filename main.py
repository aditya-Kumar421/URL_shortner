from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, URL
from schemas import URLCreate, URLInfo
from utils import generate_short_code
from config import BASE_URL

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/shorten", response_model=URLInfo)
def shorten_url(url_data: URLCreate, db: Session = Depends(get_db)):
    short_code = generate_short_code()
    while db.query(URL).filter(URL.short_code == short_code).first():
        short_code = generate_short_code()

    db_url = URL(original_url=str(url_data.url), short_code=short_code)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    return {"short_url": f"{BASE_URL}/{short_code}"}

@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(url=url_entry.original_url)