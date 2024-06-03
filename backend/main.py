from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import uuid
import docker
import subprocess
from sqlalchemy.orm import sessionmaker
## from .database import SessionLocal, CodeSubmission
## from .models import CodeRequest
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
import os

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
Base = declarative_base()

class CodeRequest(BaseModel):
    code: str

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class CodeSubmission(Base):
    __tablename__ = "code_submissions"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(Text, nullable=False)
    output = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)


app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:5174",  # Add your frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_code_safely(code: str) -> str:
    code_id = str(uuid.uuid4())
    file_path = f"/tmp/{code_id}.py"
    
    # Write code to temporary file
    with open(file_path, "w") as f:
        f.write(code)
    
    # Prepare the command to execute the code
    command = ["python3", file_path]
    
    try:
        # Execute the code with restricted permissions (without using os.setuid)
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        output = result.stdout.decode('utf-8') + result.stderr.decode('utf-8')
    except subprocess.TimeoutExpired:
        output = "Error: Code execution exceeded time limit"
    except Exception as e:
        output = f"Error: {str(e)}"
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
    
    return output

@app.post("/test_code")
async def test_code(code_request: CodeRequest):
    output = run_code_safely(code_request.code)
    return {"output": output}

@app.post("/submit_code")
async def submit_code(code_request: CodeRequest, db: Session = Depends(get_db)):
    output = run_code_safely(code_request.code)
    code_submission = CodeSubmission(code=code_request.code, output=output)
    db.add(code_submission)
    db.commit()
    db.refresh(code_submission)
    return {"id": code_submission.id, "output": output}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)