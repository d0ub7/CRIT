from prompt_toolkit.validation import Validator, ValidationError

class WordValidator(Validator):
    def __init__(self, validation_list):
        self.validation_list = validation_list
    
    def validate(self, document) -> None:
        text = document.text
        vlist = self.validation_list

        if text not in vlist:
            raise ValidationError(message='Invalid input')

class NumberValidator(Validator):
    def validate(self, document):
        text = document.text

        if text and not text.isdigit():
            i = 0

            # Get index of first non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if not c.isdigit():
                    break

            raise ValidationError(message='This input contains non-numeric characters',
                                  cursor_position=i
            )

class ItemValidator(Validator):
    def __init__(self, validation_list) -> None:
        self.validation_list = validation_list

    def validate(self, document):
        text = document.text
        vlist = self.validation_list

        if text in vlist:
            raise ValidationError(message='may not have two items of the same name')