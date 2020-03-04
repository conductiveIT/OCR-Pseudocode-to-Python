# OCR Pseudocode to Python
This is a Python program that translates code written in OCR pseudocode (as specificed in pages 31 to 35 of the specification at [OCR A Level Computer Science Specification](https://ocr.org.uk/Images/170844-specification-accredited-a-level-gce-computer-science-h446.pdf)) and executes it.

There is also a basic IDE that provides some syntax highlighting/load/save/execute/debug.

This has nothing to do with OCR and is not endorsed by them.
## Based on
This is based on [CSP-PseudocodeRunner](https://github.com/gcpreston/csp-pseudocode-runner).
## Usage
```python OCR_Pseudocode_to_Python.py ```
(defaults to looking for the pseudocode in code.txt)

Command line parameters:

```--file=foldername/file.ext``` Load the pseudocode from the file.ext in folder foldername

```--debug``` Output the Pseudocode and the Python it is translated into before executing

```python OCR_Pseudocode_to_Python_GUI.py ```

Provides a basic IDE for creating the pseudocode.  Uses OCR_Pseudocode_to_Python.py for the actual execution.
## Limitations
Keywords **must** be in UPPERCASE as the code only checks for words in uppercase.  This is different to the OCR specification - the words are the same, it is just they must be in uppercase.

Blocks of code (if statements / loops / etc.) must be indented as per Python.

## TODO
- [x] comments using //
- [x] global keyword
- [ ] do/until
- [x] file access (open/read/write/close/EOF)
- [ ] n dimensional arrays
- [ ] byVal and byRef parameter passing
