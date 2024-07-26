import sys
from reader import reader


if __name__ == "__main__":
    doc_reader = reader()
    document_path = "C:\Personal\log_correlator\Windows_2k.log"  
    doc_content, doc_name, doc_type = doc_reader.load_document(document_path)
    output_csv_path = "C:\Personal\log_correlator\csv_pdf_csv_output.csv" 
    doc_reader.convert_to_csv(doc_content, output_csv_path)