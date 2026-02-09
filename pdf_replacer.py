import pymupdf as pm
import csv
import argparse
import os
import sys
import logging

from pymupdf import Page
from pymupdf.mupdf import PDF_ANNOT_FREE_TEXT

# CLI Args
parser = argparse.ArgumentParser(description="Example script")
parser.add_argument("-p", "--pdf-file", required=True, help="Path to the PDF file")
parser.add_argument("-c", "--csv-file", required=True, help="Path to the CSV file")
parser.add_argument("-o", "--outdir", default="out", help="Output directory")
parser.add_argument("-d", "--delimiter", default=",", help="CSV delimiter (default: ',')")
parser.add_argument(
    "-P",
    "--prefix",
    default="#",
    help="Set the prefix used to mark annotation as to be replaced (default: #)"
)
parser.add_argument(
    "-f",
    "--fail",
    default=True,
    help="Fail if hitting an annotation which is marked to be replaced but not in the CSV (default: True)"
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Print DEBUG"
)
args = parser.parse_args()

# Logging
log_level = logging.DEBUG if args.verbose else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt = "%H:%M:%S"
)

if not os.path.isfile(args.pdf_file):
    sys.exit(f"Error: -p file does not exist or is not a file: {args.pdf_file}")

if not os.path.isfile(args.csv_file):
    sys.exit(f"Error: -c file does not exist or is not a file: {args.csv_file}")

if not os.path.isdir(args.outdir):
    sys.exit(f"Error: -o directory does not exist or is not a directory: {args.outdir}")


csv_file = csv.DictReader(open(args.csv_file), delimiter=args.delimiter)

for (idx, row) in enumerate(csv_file):
    # Repeatedly load the file, probably not very smart
    doc = pm.open(args.pdf_file)

    logging.info(f"Start replacing for row {idx}")

    page: Page
    for page in doc.pages():
        for annot in page.annots():
            if annot.type[0] != PDF_ANNOT_FREE_TEXT:
                logging.debug(f"Ignoring annotation not of PDF_ANNOT_FREE_TEXT type")
                continue

            text: str = annot.info["content"]
            if not text.startswith("#"):
                logging.debug(f"Ignoring annotation (text: '{text}') because it doesn't start with {args.prefix}")
                continue
            logging.debug(f"Processing annotation (text: '{text}') because it starts with {args.prefix}")

            key = text.strip(args.prefix)
            if not key in row and args.fail:
                sys.exit(f"Encountered an annotation (text: '{text}') for who's key '{key}' we don't have a value in the CSV")
            elif not key in row and not args.fail:
                # Just ignore it
                continue

            value = row[key]
            rect = annot.rect
            page.delete_annot(annot)
            page.add_freetext_annot(rect, value)
            #annot.update(text=value)
            logging.info(f"For row #{idx} replaced '{text}' with '{value}'")

    doc.save(f"{args.outdir}/output-{idx}.pdf")

