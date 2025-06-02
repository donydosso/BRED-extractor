import re
import json
import pandas as pd
import sys
import pdfplumber

def clean_number(num_str):
    """Nettoie et convertit une chaîne numérique avec séparateurs de milliers"""
    if not num_str or str(num_str).strip() == '':
        return 0.0
    try:
        # Remplace les points de milliers et les virgules décimales
        cleaned = str(num_str).replace('.', '').replace(',', '.')
        return float(cleaned)
    except ValueError:
        return 0.0

def is_empty_transaction(transaction):
    """Vérifie si une transaction n'a ni débit ni crédit"""
    debit_empty = (transaction.get('debit', 0) == 0)
    credit_empty = (transaction.get('credit', 0) == 0)
    return debit_empty and credit_empty

def parse_pdf_to_data(pdf_path):
    compte_principal = []
    agios = []
    frais_commissions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            tables = page.extract_tables()
            
            # Page 1 - Compte principal et agios
            if "Relevé d'opérations du poste principal" in text:
                # Table des opérations principales
                if len(tables) > 1:
                    op_table = tables[1]
                    for row in op_table[1:]:
                        if len(row) >= 5 and row[0] and not any(x in str(row[0]).lower() for x in ["date", "total"]):
                            try:
                                if "\n" in row[0]:  # Lignes multiples
                                    dates = row[0].split("\n")
                                    libelles = row[1].split("\n")
                                    debits = row[2].split("\n") if row[2] else []
                                    credits = row[3].split("\n") if row[3] else []
                                    
                                    for i in range(len(dates)):
                                        transaction = {
                                            "date": dates[i].strip(),
                                            "libelle": libelles[i].strip() if i < len(libelles) else "",
                                            "debit": clean_number(debits[i]) if i < len(debits) else 0,
                                            "credit": clean_number(credits[i]) if i < len(credits) else 0,
                                            "type": "transaction"
                                        }
                                        if not is_empty_transaction(transaction):
                                            compte_principal.append(transaction)
                                else:  # Ligne simple
                                    op_type = "solde_initial" if "Solde précédent" in row[1] else (
                                             "solde_final" if "Nouveau solde" in row[1] else "transaction")
                                    
                                    transaction = {
                                        "date": row[0].strip(),
                                        "libelle": row[1].strip(),
                                        "debit": clean_number(row[2]),
                                        "credit": clean_number(row[3]),
                                        "type": op_type
                                    }
                                    # On garde toujours les soldes initiaux/finaux même s'ils sont à 0
                                    if op_type in ["solde_initial", "solde_final"] or not is_empty_transaction(transaction):
                                        compte_principal.append(transaction)
                            except Exception as e:
                                print(f"Erreur traitement ligne opération: {row} - {e}")
                                continue
                
                # Table des agios
                if len(tables) > 2:
                    agios_table = tables[2]
                    for row in agios_table[1:]:
                        if len(row) >= 4 and row[0] and not any(x in str(row[0]).lower() for x in ["libellé", "---"]):
                            try:
                                if "\n" in row[0]:
                                    libelles = row[0].split("\n")
                                    debits = row[2].split("\n") if row[2] else []
                                    
                                    for i in range(len(libelles)):
                                        transaction = {
                                            "date": "31/12/2023",
                                            "libelle": libelles[i].strip(),
                                            "debit": clean_number(debits[i]) if i < len(debits) else 0,
                                            "credit": 0,
                                            "type": "agio"
                                        }
                                        if not is_empty_transaction(transaction):
                                            agios.append(transaction)
                                else:
                                    transaction = {
                                        "date": "31/12/2023",
                                        "libelle": row[0].strip(),
                                        "debit": clean_number(row[2]),
                                        "credit": 0,
                                        "type": "agio"
                                    }
                                    if not is_empty_transaction(transaction):
                                        agios.append(transaction)
                            except Exception as e:
                                print(f"Erreur traitement ligne agio: {row} - {e}")
                                continue
            
            # Page 3 - Frais et commissions
            if "Détail des frais et commissions" in text and len(tables) > 0:
                frais_table = tables[0]
                for row in frais_table[1:]:
                    if len(row) >= 6 and row[0] and not any(x in str(row[0]).lower() for x in ["date", "montant", "total"]):
                        try:
                            if "\n" in row[0]:
                                dates = row[0].split("\n")
                                libelles = row[1].split("\n")
                                montants = row[5].split("\n") if len(row) > 5 and row[5] else []
                                
                                for i in range(len(dates)):
                                    transaction = {
                                        "date": dates[i].strip(),
                                        "libelle": libelles[i].strip() if i < len(libelles) else "",
                                        "debit": clean_number(montants[i]) if i < len(montants) else 0,
                                        "credit": 0,
                                        "type": "frais"
                                    }
                                    if not is_empty_transaction(transaction):
                                        frais_commissions.append(transaction)
                            else:
                                transaction = {
                                    "date": row[0].strip(),
                                    "libelle": row[1].strip(),
                                    "debit": clean_number(row[5]) if len(row) > 5 and row[5] else 0,
                                    "credit": 0,
                                    "type": "frais"
                                }
                                if not is_empty_transaction(transaction):
                                    frais_commissions.append(transaction)
                        except Exception as e:
                            print(f"Erreur traitement ligne frais: {row} - {e}")
                            continue

    return compte_principal, agios, frais_commissions

def save_to_excel(data, excel_path):
    compte_principal, agios, frais_commissions = data
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Compte principal
        df_compte = pd.DataFrame(compte_principal)
        df_compte.to_excel(writer, sheet_name='Compte Principal', index=False)
        
        # Agios
        df_agios = pd.DataFrame(agios)
        df_agios.to_excel(writer, sheet_name='Agios', index=False)
        
        # Frais et commissions
        df_frais = pd.DataFrame(frais_commissions)
        df_frais.to_excel(writer, sheet_name='Frais et Commissions', index=False)

def save_to_json(data, json_path):
    compte_principal, agios, frais_commissions = data
    
    output = {
        "compte_principal": compte_principal,
        "agios": agios,
        "frais_commissions": frais_commissions
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 app.py <input_pdf> <output_excel> <output_json>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    excel_path = sys.argv[2]
    json_path = sys.argv[3]
    
    print(f"Traitement du fichier: {pdf_path}")
    data = parse_pdf_to_data(pdf_path)
    save_to_excel(data, excel_path)
    save_to_json(data, json_path)
    
    print(f"\nRésultats d'extraction:")
    print(f"- Opérations compte principal: {len(data[0])}")
    print(f"- Lignes d'agios: {len(data[1])}")
    print(f"- Frais et commissions: {len(data[2])}")

if __name__ == "__main__":
    main()