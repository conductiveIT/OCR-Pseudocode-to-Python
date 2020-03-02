# OCR Pseudocode to Python
This is a Python program that translates code written in OCR pseudocode (as specificed in pages 31 to 35 of the specification at [OCR A Level Computer Science Specification](https://ocr.org.uk/Images/170844-specification-accredited-a-level-gce-computer-science-h446.pdf)) and executes it.
## Based on
This is based on [CSP-PseudocodeRunner](https://github.com/gcpreston/csp-pseudocode-runner).
## Usage
```python OCR-Pseudocode-to-Python.py ```
(defaults to looking for the pseudocode in code.txt)

Command line parameters:

```--file=foldername/file.ext``` Load the pseudocode from the file.ext in folder foldername

```--debug``` Output the Pseudocode and the Python it is translated into before executing

## Limitations
Keywords **must** be in UPPERCASE as the code only checks for words in uppercase.  This is different to the OCR specification - the words are the same, it is just they must be in uppercase.

## TODO
- [x] comments using //
- [ ] global keyword
- [ ] do/until
- [x] file access (open/read/write/close/EOF)
- [ ] n dimensional arrays
- [ ] byVal and byRef parameter passing
