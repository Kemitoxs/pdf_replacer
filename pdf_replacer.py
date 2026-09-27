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
parser.add_argument(
    "-d", "--delimiter", default=",", help="CSV delimiter (default: ',')"
)
parser.add_argument(
    "-P",
    "--prefix",
    default="#",
    help="Set the prefix used to mark annotation as to be replaced (default: #)",
)
parser.add_argument(
    "-f",
    "--fail",
    default=True,
    help="Fail if hitting an annotation which is marked to be replaced but not in the CSV (default: True)",
)
parser.add_argument("-v", "--verbose", action="store_true", help="Print DEBUG")
parser.add_argument(
    "-a", "--appendix-col", help="Which column to use to set the attachment file."
)
parser.add_argument(
    "-s",
    "--sort-by",
    help="Sort by a column either ascending or descending. Format: 'a,<COLUMN_NAME>' or 'd,<COLUMN_NAME>",
)
args = parser.parse_args()

# Logging
log_level = logging.DEBUG if args.verbose else logging.INFO
logging.basicConfig(
    level=log_level,
    format="[%(asctime)s %(levelname)s]: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")

if not os.path.isfile(args.pdf_file):
    sys.exit(f"Error: -p file does not exist or is not a file: {args.pdf_file}")

if not os.path.isfile(args.csv_file):
    sys.exit(f"Error: -c file does not exist or is not a file: {args.csv_file}")

if not os.path.isdir(args.outdir):
    sys.exit(f"Error: -o directory does not exist or is not a directory: {args.outdir}")

descending, sort_by_column = args.sort_by.split(",")
descending = descending == "d"

csv_file = csv.DictReader(
    open(args.csv_file, encoding="utf-8-sig"), delimiter=args.delimiter
)
rows = list(csv_file)

if sort_by_column is not None:
    rows = sorted(rows, key=lambda row: row[sort_by_column], reverse=descending)

for idx, row in enumerate(rows):
    # Repeatedly load the file, probably not very smart
    doc = pm.open(args.pdf_file)

    logger.info(f"Start replacing for row {idx}")

    page: Page
    for page in doc.pages():
        for annot in page.annots():
            if annot.type[0] != PDF_ANNOT_FREE_TEXT:
                logger.debug("Ignoring annotation not of PDF_ANNOT_FREE_TEXT type")
                continue

            text: str = annot.info["content"]
            if not text.startswith(args.prefix):
                logger.debug(
                    f"Ignoring annotation (text: '{text}') because it doesn't start with {args.prefix}"
                )
                continue

            logger.debug(
                f"Processing annotation (text: '{text}') because it starts with {args.prefix}"
            )

            key = text.strip(args.prefix)
            if not key in row and args.fail:
                sys.exit(
                    f"Encountered an annotation (text: '{text}') for who's key '{key}' we don't have a value in the CSV"
                )
            elif not key in row and not args.fail:
                # Just ignore it
                continue

            value = row[key]
            rect = annot.rect
            page.delete_annot(annot)
            page.add_freetext_annot(rect, value)
            # annot.update(text=value)
            logger.debug(f"For row #{idx} replaced '{text}' with '{value}'")

    if args.appendix_col is not None and args.appendix_col in row:
        file_name = row[args.appendix_col]
        appendix = pm.open(file_name)
        doc.insert_pdf(appendix)
        logger.debug(f"Attached '{file_name}'")

    doc.save(f"{args.outdir}/output-{idx}.pdf")
