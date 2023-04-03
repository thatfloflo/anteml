"""AnTeML entities."""

entities: dict[str, tuple[str, str]] = {
    # Name     Value   Description  
    "ESC":  ("\x1b", "Escape character"),
    "CSI":  ("\x9b", "Control sequence introducer"),
    "DCS":  ("\x90", "Device control string"),
    "OSC":  ("\x9d", "Operating system command"),

    "ST":   ("\x9c", "String Terminator"),
    "SOS":  ("\x98", "Start of string"),
    "PM":   ("\x9e", "Privacy message"),
    "APC":  ("\x9f", "Application program command"),

    "BEL":  ("\x07", "Terminal bell"),
    "BS":   ("\x08", "Backspace"),
    "HT":   ("\x09", "Horizontal tab"),
    "LF":   ("\x0a", "Linefeed"),
    "VT":   ("\x0b", "Vertical tab"),
    "FF":   ("\x0c", "Form feed"),
    "CR":   ("\x0d", "Carriage return"),
    "DEL":  ("\x7f", "Delete character"),

    "amp":  ("&", "Ampersand"),
    "lt":   ("<", "Less than"),
    "gt":   (">", "Greater than"),
    "nbsp": (" ", "Non-breaking space"),
}