from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database.database import engine, get_db
from app.models import models
from app.routes import auth, materials, users, dashboard
from app.dependencies import get_optional_user, get_current_user
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quản lý Học liệu Trường Sĩ quan Chính trị")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(materials.router, prefix="/api", tags=["materials"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(dashboard.router, tags=["dashboard"])  # Dashboard router already has /api prefix in routes

# Routes
@app.get("/")
async def index(
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_optional_user)
):
    # Redirect to login if not authenticated
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Redirect to dashboard (dashboard is now the home page)
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/materials")
async def materials_page(
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_optional_user)
):
    # Redirect to login if not authenticated
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get all departments
    departments = db.query(models.Department).all()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "departments": departments
    })

@app.get("/login")
async def login_page(request: Request, user = Depends(get_optional_user)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)  # Redirect to dashboard instead of /
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request, user = Depends(get_optional_user)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)  # Redirect to dashboard instead of /
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/detail")
async def detail_page(
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_optional_user)
):
    # Redirect to login if not authenticated
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get all departments for the detail page
    departments = db.query(models.Department).all()
    
    return templates.TemplateResponse("detail.html", {
        "request": request,
        "user": user,
        "departments": departments
    })

@app.get("/dashboard")
async def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_optional_user)
):
    # Redirect to login if not authenticated
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get all departments
    departments = db.query(models.Department).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "departments": departments
    })

@app.get("/statistics")
async def statistics_page(
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_optional_user)
):
    # Redirect to login if not authenticated
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get all departments
    departments = db.query(models.Department).all()
    
    return templates.TemplateResponse("statistics.html", {
        "request": request,
        "user": user,
        "departments": departments
    })

# Initialize departments on startup
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    
    # Check if departments exist
    existing_depts = db.query(models.Department).count()
    
    if existing_depts == 0:
        # Create default departments
        departments_data = [
            {"code": "K1", "name": "Khoa Triết học Mác - Lênin"},
            {"code": "K2", "name": "Khoa Lịch sử Đảng Cộng sản Việt Nam"},
            {"code": "K3", "name": "Khoa Công tác Đảng, Công tác Chính trị"},
            {"code": "K4", "name": "Khoa Chiến thuật"},
            {"code": "K5", "name": "Khoa Văn hóa - Ngoại ngữ"},
            {"code": "K6", "name": "Khoa Kinh tế chính trị Mác - Lênin"},
            {"code": "K7", "name": "Khoa Chủ nghĩa xã hội khoa học"},
            {"code": "K8", "name": "Khoa Tâm lý học quân sự"},
            {"code": "K9", "name": "Khoa Bắn súng"},
            {"code": "K10", "name": "Khoa Quân sự chung"},
            {"code": "K11", "name": "Khoa Giáo dục thể chất"},
            {"code": "K12", "name": "Khoa Sư phạm quân sự"},
            {"code": "K13", "name": "Khoa Tư tưởng Hồ Chí Minh"},
            {"code": "K14", "name": "Khoa Nhà nước & Pháp luật"},
        ]
        
        for dept_data in departments_data:
            dept = models.Department(**dept_data)
            db.add(dept)
        
        db.commit()
        print("✅ Đã khởi tạo 14 khoa thành công")
    
    # Create admin user if not exists
    admin_user = db.query(models.User).filter(models.User.username == "admin").first()
    
    if not admin_user:
        from app.auth import get_password_hash
        
        admin = models.User(
            username="admin",
            email="admin@sqct.edu.vn",
            full_name="Quản trị viên",
            hashed_password=get_password_hash("admin123"),
            role=models.UserRole.ADMIN
        )
        db.add(admin)
        db.commit()
        print("✅ Đã tạo tài khoản admin (username: admin, password: admin123)")
    
    db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
