import docx


def get_underlying_element(element):
    """
    get the actual underlying element of the given element
    if it's indeed an element, return itself
    """
    if element is None:
        return None
    return getattr(element, "_element", element)


def replace_text(paragraph, old_text, new_text):
    """
    replace the old text with new text in the given paragraph
    without changing the text style
    """
    new_text = "" if new_text is None else str(new_text)
    runs = paragraph.runs
    if len(runs) == 0:
        return
    runs[0].text = paragraph.text.replace(old_text, new_text)
    runs[0].font.color.rgb = docx.shared.RGBColor(0, 0, 0)
    for run in runs[1:]:
        run.text = ""


def remove_element(element):
    """
    remove the given element from its parent
    """
    element = get_underlying_element(element)
    if element is None:
        return
    parent = element.getparent()
    if parent is not None and element in parent:
        parent.remove(element)
