import os
import sys

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: pypdf not installed. Attempting to install...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    from pypdf import PdfReader

pdf_path = "Enunciado_Control_Volumen_Manos.pdf"
output_path = "enunciado.txt"

try:
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {os.path.abspath(pdf_path)}")
        sys.exit(1)
        
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Success: Content written to {os.path.abspath(output_path)}")
    print("--- CONTENT START ---")
    print(text[:2000]) # Print first 2000 chars
    print("--- CONTENT END ---")
except Exception as e:
    print(f"Error reading PDF: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
