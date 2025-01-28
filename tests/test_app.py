import pytest
from fastapi.testclient import TestClient
from app import app
import os

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_check_api_key():
    response = client.get("/check-api-key")
    assert response.status_code == 200
    assert "hasKey" in response.json()

def test_set_api_key():
    test_key = "test-api-key"
    response = client.post(
        "/set-api-key",
        json={"api_key": test_key}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Clean up
    if os.path.exists(".env"):
        os.remove(".env")

@pytest.mark.asyncio
async def test_upload_file():
    # Create a test PDF file
    test_pdf_content = b"%PDF-1.0\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
    with open("test.pdf", "wb") as f:
        f.write(test_pdf_content)
    
    # Test file upload
    with open("test.pdf", "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("test.pdf", f, "application/pdf")}
        )
    assert response.status_code == 200
    
    # Clean up
    os.remove("test.pdf")
    
def test_ask_without_upload():
    response = client.post(
        "/ask",
        json={"question": "Test question"}
    )
    assert response.status_code == 400

def test_summarize_without_upload():
    response = client.get("/summarize")
    assert response.status_code == 400

def test_generate_faq_without_upload():
    response = client.get("/generate-faq")
    assert response.status_code == 400