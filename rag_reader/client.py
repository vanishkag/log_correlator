import sys
from reader import reader


def main(file_path):
    reader_obj = reader()
    documents = reader_obj.load_document(file_path)
    print("Loaded Document: ")
    for document in documents:
        print(document)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 client.py path_to_pdf_file")
    else:
        file_path = sys.argv[1]
        main(sys.argv[1])
