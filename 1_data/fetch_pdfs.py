import sys
import os
import json
import pdfplumber
import requests
from io import BytesIO
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import JRC_API_BASE

RAW_DIR = ROOT_DIR / "1_data" / "raw"
PROCESSED_DIR = ROOT_DIR / "1_data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def extract_pdf_text(url: str, max_chars: int = 4000) -> str:
    try:
        resp = requests.get(url, timeout=10)
        with pdfplumber.open(BytesIO(resp.content)) as pdf:
            text = ""
            for page in pdf.pages[:8]:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text[:max_chars].strip()
    except Exception:
        return ""

def main():
    datasets_file = ROOT_DIR / "1_data" / "jrc_datasets.json"
    if not datasets_file.exists():
        print("1_data/jrc_datasets.json not found. Running fetch_jrc.py first.")
        import fetch_jrc
        fetch_jrc.main()

    with open(datasets_file, "r", encoding="utf-8") as f:
        datasets = json.load(f)

    documents = []
    category_counts = {}
    years = []
    manifest_docs = []

    for ds in datasets:
        category = ds.get("category", "general_transport")
        year = ds.get("publication_year", 2023)
        category_counts[category] = category_counts.get(category, 0) + 1
        years.append(year)

        doc_text = f"""
Title: {ds['title']}
Organization: {ds['organization']}
Source URL: {ds['url']}
Category: {category}
Publication Year: {year}
Tags: {', '.join(ds['tags'])}

Description:
{ds['notes']}

Available Resources:
""".strip()
        for r in ds["resources"]:
            doc_text += f"\n- {r['name']} ({r['format']}): {r['description']}"

        pdf_text = ""
        for r in ds["resources"]:
            if r.get("format", "").upper() == "PDF" and r.get("url"):
                print(f"  Extracting PDF: {r['name']}")
                pdf_text = extract_pdf_text(r["url"])
                if pdf_text:
                    break

        doc_item = {
            "id": ds["id"],
            "title": ds["title"],
            "category": category,
            "publication_year": year,
            "organization": ds["organization"],
            "url": ds["url"],
            "metadata_text": doc_text,
            "pdf_text": pdf_text,
            "tags": ds["tags"],
        }
        documents.append(doc_item)

        manifest_docs.append({
            "document_id": ds["id"],
            "title": ds["title"],
            "category": category,
            "publication_year": year,
            "source": ds["organization"],
            "url": ds["url"],
            "tags": ds["tags"],
        })
        print(f"Processed: [{category} | {year}] {ds['title'][:60]}")

    # Write processed documents to root and processed folder
    processed_doc_path = PROCESSED_DIR / "processed_documents.json"
    root_doc_path = ROOT_DIR / "1_data" / "jrc_documents.json"

    with open(processed_doc_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    with open(root_doc_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    # Generate corpus manifest
    corpus_manifest = {
        "total_documents": len(documents),
        "total_categories": len(category_counts),
        "categories": category_counts,
        "year_range": {
            "min": min(years) if years else 2023,
            "max": max(years) if years else 2024
        },
        "created_at": datetime.now().isoformat(),
        "documents_manifest": manifest_docs
    }

    manifest_path = ROOT_DIR / "1_data" / "corpus_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(corpus_manifest, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(documents)} documents to {root_doc_path}")
    print(f"Saved Corpus Manifest to {manifest_path}")

if __name__ == "__main__":
    main()
