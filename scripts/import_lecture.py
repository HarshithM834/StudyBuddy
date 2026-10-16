"""Import a lecture without copying course material into version control."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server.app import database, import_pdf

parser = argparse.ArgumentParser()
parser.add_argument("pdf", type=Path)
parser.add_argument("--course", default="Your course")
parser.add_argument("--week6", action="store_true", help="Enable the verified Hamming lab for the supplied CYSE 425 Week 6 deck")
args = parser.parse_args()
document = import_pdf(args.pdf.read_bytes(), args.pdf.name, args.course, "cyse425-week6" if args.week6 else None)
if args.week6:
    titles = {19: "Parity checking", 20: "Hamming distance", 21: "Hamming: building the code", 22: "Hamming: checking the message", 23: "Hamming: finding the error", 24: "SSID", 25: "BSSID", 26: "Basic service set", 27: "Extended service set", 28: "Roaming between access points", 30: "Wi-Fi discovery", 31: "Probe request", 32: "Probe response", 33: "Authentication", 34: "Association", 35: "Wi-Fi connection sequence", 36: "Symmetric cryptosystem"}
    with database() as db:
        for page, title in titles.items():
            db.execute("UPDATE pages SET title=? WHERE document_id=? AND number=?", (title, document["id"], page))
print(f"Imported {document['name']}: {document['page_count']} slides ({document['id']}).")
