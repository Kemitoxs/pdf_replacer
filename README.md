# PDF Replacer

Replace annotations in a PDF with rows of a CSV file.

Add free text annotations to your PDF file and starting with a prefix (default #).
For each row the script will generate a new PDF file where each annotation with the prefix
(default #) will be replaced with the corresponding value in that row.

Give the Python script:
- the PDF file to replace in (`-p` parameter)
- the CSV file to replace from (`-c` parameter)

## Examples

Simple Replace: `python3 pdf_replacer.py -p input.pdf -c input.csv`

Advanced, you can also change the CSV delimiter and PDF prefix:  
```
python3 pdf_replacer.py 
    -p input.pdf  
    -c input.csv  
    -o out  # Out directory
    -d " "  # CSV delimiter
    -P "$"  # PDF prefix
    -f false 
    -v  # Verbose logging
```

