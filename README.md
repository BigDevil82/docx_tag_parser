# DocxTagParser
A simple demo to parse IF-ELSE tags in a template docx file.

## outline
A docx template file is prepared in advance with IF-ELSE tags.
The script is used to find those tags and check conditions in it.
If the condition is true, the content enclosed by IF tag part is kept, otherwise it is removed.

## file structure
- `template.docx`: the template file with IF-ELSE tags
- `tag_parser.py`: the main script to parse the tags in the template file
- `data_manager.py`: the script to manage data context for retrieving data to check conditions.
  it's simplified in this demo.
- `util.py`: the script to provide some utility functions for the demo.

