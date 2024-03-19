import enum
import re

import docx

from data_manager import DataContextManager
from util import remove_element, replace_text


class IfElseSearchStatus(enum.Enum):
    """
    search status for if else tag
    """

    NONE = 0
    FOUND_IF = 1
    FOUND_ELSE = 2
    FOUND_END = 3


class IfElseTagParser:
    """
    parse IF ELSE tags in an docx tempate document
    replace content in it based on the condition
    remain the content if the condition is satisfied else remove the content

    Args:
     - doc (docx.Document): the docx document to parse
     - data_manager (DataContextManager): the data manager to get the data from
       which is used to check the if else condition
    """

    def __init__(self, doc, data_manager: DataContextManager) -> None:
        self.doc = doc
        self.data_manager = data_manager

        self.status = IfElseSearchStatus.NONE  # search status
        self.if_satisfied = False  # if the if condition is satisfied
        self.element_discard = False  # if the element should be discarded

        self._comiple_regex()

    def _comiple_regex(self):
        self.if_start = re.compile(r"^\s*<IF *=([\w=]+)>")
        self.else_tag = re.compile(r"^\s*<ELSE>")  # else tag is optional
        self.if_end = re.compile(r"^\s*</IF>")
        self.inline_if = re.compile(r"<IF *=([\w=]+)>(.+)</IF>")
        self.inline_if_else = re.compile(r"<IF *=([\w=]+)>(.+)<ELSE>(.+)</IF>")

    def check_if_condition(self, condition: str):
        """
        check if the condition is satisfied

        Args:
         - condition (str): the condition str in IF tag
        """

        if "=" in condition:
            self.check_key, check_value = condition.split("=")
        else:
            self.check_key, check_value = condition, None

        real_value = self.data_manager.get_json_value(self.check_key)
        if check_value is None:
            return real_value
        else:
            return real_value == check_value

    def check_inline_if(self, paragraph):
        if paragraph is None:
            return

        if res := self.inline_if_else.search(paragraph.text):
            for res in self.inline_if_else.finditer(paragraph.text):
                key, if_val, else_val = res.group(1), res.group(2), res.group(3)
                if_satisfied = self.check_if_condition(key)
                if if_satisfied:
                    replace_text(paragraph, res.group(), if_val)
                else:
                    replace_text(paragraph, res.group(), else_val)
        elif res := self.inline_if.search(paragraph.text):
            for res in self.inline_if.finditer(paragraph.text):
                key, value = res.group(1), res.group(2)
                if_satisfied = self.check_if_condition(key)
                if if_satisfied:
                    replace_text(paragraph, res.group(), value)
                else:
                    replace_text(paragraph, res.group(), "")

    def remove_element(self, element):
        remove_element(element)
        self.element_discard = True

    def _check_status(self, docx_element, paragraph=None):
        """
        check if the element is in the IF-ELSE tag

        Args:
         - docx_element: the docx element to check
         - paragraph: the paragraph docx element

        Returns:
            - bool: if the element is in the IF-ELSE tag
        """

        if self.status == IfElseSearchStatus.FOUND_IF and not self.if_satisfied:
            self.remove_element(docx_element)
            return True

        if self.status == IfElseSearchStatus.FOUND_IF and self.if_satisfied:
            self.check_inline_if(paragraph)
            return True

        if self.status == IfElseSearchStatus.FOUND_ELSE and self.if_satisfied:
            self.remove_element(docx_element)
            return True

        if self.status == IfElseSearchStatus.FOUND_ELSE and not self.if_satisfied:
            self.check_inline_if(paragraph)
            return True

        return False

    def process_element(self, docx_element):
        """
        entry point to process the docx element
        those elements satisfying the condition will be kept
        and those not satisfying the condition will be removed
        IF-ELSE tag will be removed as well

        Args:
         - docx_element: the docx element to process
        """
        self.element_discard = False
        if isinstance(docx_element, docx.oxml.text.paragraph.CT_P):
            paragraph = docx.text.paragraph.Paragraph(docx_element, self.doc)
            text = paragraph.text

            if res := self.if_start.search(text):
                # self.current_tag = res.group(1)
                self.status = IfElseSearchStatus.FOUND_IF
                self.if_satisfied = self.check_if_condition(res.group(1))
                self.remove_element(docx_element)
                return

            if self.else_tag.search(text):
                self.status = IfElseSearchStatus.FOUND_ELSE
                self.remove_element(docx_element)
                return

            if self.if_end.search(text):
                self.status = IfElseSearchStatus.FOUND_END
                self.remove_element(docx_element)
                return

            is_in_existing_tag = self._check_status(docx_element, paragraph)
            if is_in_existing_tag:
                return

            self.check_inline_if(paragraph)
        else:
            self._check_status(docx_element, None)


if __name__ == "__main__":
    doc = docx.Document("template.docx")
    data_manager = DataContextManager("data.json")  # not provided in this repo
    parser = IfElseTagParser(doc, data_manager)
    for element in doc.element.body:
        parser.process_element(element)
    doc.save("report_parsed.docx")
