from typing import Union


class Element:
    def __init__(self, by_method: str, by_value: str, value: Union[str, int, bool, float] = ""):
        """
            Recording input values and obtaining DOM elements methods.

            Parameters:
                by_method: Method to obtain DOM elements.
                by_value: The value required for the method to obtain DOM elements.
                value: The value to be entered in the input field.
        """
        self.by_method = by_method
        self.by_value = by_value
        self.value = value
