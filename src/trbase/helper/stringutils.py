

def camel_case_to_pythonic(string: str) -> str:
    """
    Convert string in CamelCase to pythonic name.

    Example:
         HorstWasHere -> horst_was_here
    """
    if not string:
        return string
    new = ''.join([f'_{letter.lower()}' if letter.isupper() else letter for letter in string])
    new = new[1:] if new.startswith('_') else new
    new = f'n{new}' if new[0].isdigit() else new
    return new
