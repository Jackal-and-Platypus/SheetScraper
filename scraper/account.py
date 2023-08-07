from typing import Optional
from scraper.test_suite import TestSuite
from scraper.element import Element


class Account:
    def __init__(self, test_suite: TestSuite, login_id: Element, password: Element):
        self.test_suite = test_suite
        self.login_id = login_id
        self.password = password

    def signup(self, url: str, form_e: Element, params: Optional[list[Element]] = None):
        """
            Parameters:
                url (str): Register url
                form_e (Element): submit element of the form
                params (list[Element]): Other fields required during registration
        """
        self.go_submit_form_with_account(url, form_e, params)

    def signin(self, url: str, form_e: Element, params: Optional[list[Element]] = None):
        """
            Parameters:
                url (str): Register url
                form_e (Element): submit element of the form
                params (list[Element]): Other fields required during login
        """
        self.go_submit_form_with_account(url, form_e, params)

    def del_account(self, url: str, button_e: Element):
        self.test_suite.jump_to_page(url)
        self.test_suite.click_button(button_e)

    def go_submit_form_with_account(self, url: str, form_e: Element, params: Optional[list[Element]] = None):
        params = params or []
        params.insert(0, self.login_id)
        params.insert(1, self.password)
        self.test_suite.go_submit_form_with_params(url, form_e, params)
