import pdfplumber

with pdfplumber.open( "../go/tmp/uploads/Releveì n°1 dateì du 12 janvier 2024 .pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"\n=== Page {i+1} ===")
        print("Texte brut:")
        print(page.extract_text())
        
        print("\nTables détectées:")
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"\nTable {j+1}:")
            for row in table:
                print(row)