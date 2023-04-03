from typing import ClassVar, Literal, Pattern
import re


class Color:
    """Color values.

    This class offers methods for parsing and interpreting AnTeML #COLOR value
    strings.

    #COLOR value strings can be one of:
        - The literals "BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA",
            "CYAN", or "WHITE".
        - Literal "D" followed by a decimal number between 0 and 255, e.g.
            "D0", "D28", "D255".
        - Literal "X" followed by hex triplet for RGB values as either RGB or
            RRGGBB, e.g. "X333" (=0x333333) or "XA03F22" (=0xA03F22).
    """

    names: ClassVar[dict[str, tuple[str, str]]] = {
      # Name        fg-dec  bg-dec
        "black":    ("30",  "40"),
        "red":      ("31",  "41"),
        "green":    ("32",  "42"),
        "yellow":   ("33",  "43"),
        "blue":     ("34",  "44"),
        "magenta":  ("35",  "45"),
        "cyan":     ("36",  "46"),
        "white":    ("37",  "47"),
        "default":  ("39",  "49"),
    }

    decimal_pattern: ClassVar[Pattern[str]] = re.compile(
        r"\AD(?:\d{1,2}|(?:[01]?\d{2})|(?:2[0-4]\d)|(?:25[0-5]))\Z",
        re.IGNORECASE
    )

    hex_pattern: ClassVar[Pattern[str]] = re.compile(
        r"\AX(?:[0-9A-F]{3}|[0-9A-F]{6})\Z",
        re.IGNORECASE
    )

    cache: ClassVar[
        dict[
            str,
            tuple[
                Literal["name", "decimal", "hex"],
                str,
                str
            ] | None
        ]
    ] = {}

    @classmethod
    def clear_cache(cls):
        """Clear the color lookup cache."""
        cls.cache = {}

    @classmethod
    def parse(cls, value: str) -> tuple[Literal["name", "decimal", "hex"], str, str] | None:
        """Parse and cache a color value string.

        Checks if the value has already been cached first, and if so returns
        the cached values. Otherwise parses the string, adds the value to the
        cache and then returns it.
        
        Returns: A tuple containing the triplet "type" ("name", "fg_value",
        "bg_value"), or `None` if *value* is not a valid color value string.
        """
        value = value.lower()
        if value in cls.cache:
            return cls.cache[value]
        if value in cls.names:
            cls.cache[value] = ("name", cls.names[value][0], cls.names[value][1])
        elif match := cls.decimal_pattern.fullmatch(value):
            v = match[0][1:].lstrip("0")
            cls.cache[value] = ("decimal", v, v)
        elif match := cls.hex_pattern.fullmatch(value):
            v = match[0][1:].lower()
            if len(v) == 3:
                v = "".join([f"{c}{c}" for c in v])
            cls.cache[value] = ("hex", v, v)
        else:
            cls.cache[value] = None
        return cls.cache[value]

    @classmethod
    def type(cls, value: str) -> Literal["name", "decimal", "hex"] | None:
        """Determine the color string type."""
        if parsed := cls.parse(value):
            return parsed[0]
        return None

    @classmethod
    def fg_value(cls, value: str) -> str | None:
        """Determine the foreground value of a color string."""
        if parsed := cls.parse(value):
            return parsed[1]
        return None

    @classmethod
    def bg_value(cls, value: str) -> str | None:
        """Determine the foreground value of a color string."""
        if parsed := cls.parse(value):
            return parsed[2]
        return None


class FontWeight:
    """FontWeight values.

    This class offers methods for parsing and interpreting AnTeML #FONTWEIGHT
    value strings.

    #FONTWEIGHT value strings can be one of:
        - The literals "BOLD", "NORMAL", or "LIGHT".
    """

    weights: ClassVar[dict[str, str]] = {
      # Name        code
        "bold":     "1",
        "normal":   "22",
        "light":    "2",
        "default":  "22",
    }

    @classmethod
    def parse(cls, value: str) -> str | None:
        """Parse a font weight and return corresponding ANSI value."""
        value = value.lower()
        if value in cls.weights:
            return cls.weights[value]
        return None


class Boolean:
    """Boolean values.

    Evaluates a truthy/falsy string to bool `True` or `False`.

    Truthy values: "1", "yes", "on", "true".
    Falsy values: "0", "no", "off", "false".
    """

    truthy_values: ClassVar[set[str]] = {
        "1",
        "yes",
        "on",
        "true",
    }

    falsy_values: ClassVar[set[str]] = {
        "0",
        "no",
        "off",
        "false",
    }

    @classmethod
    def parse(cls, value: str) -> bool | None:
        """Convert truthy/falsy string to boolean, or None if indeterminate."""
        value = value.lower()
        if value in cls.truthy_values:
            return True
        if value in cls.falsy_values:
            return False
        return None


class ScreenMode:
    """ScreenMode values.
    
    This class offers methods for parsing and interpreting AnTeML #SCREENMODE
    value strings.

    #SCREENMODE value strings can have one of the following values:
    * "40x24m": 40 x 25 monochrome text
    * "40x25c": 40 x 25 color text
    * "80x25m": 80 x 25 monochrome text
    * "80x25c": 80 x 25 color text
    * "320x200c4": 320 x 200 4-color graphics
    * "320x200m": 320 x 200 monochrome graphics
    * "640X200m": 640 x 200 monochrome graphics
    * "320x200c": 320 x 200 256-color graphics
    * "640x200c": 640 x 200 16-color graphics
    * "640x350m": 640 x 350 monochrome 2-color graphics
    * "640x350c": 640 x 350 16-color graphics
    * "640x480m": 640 x 480 monochrome 2-color graphics
    * "640x480c": 640 x 480 16-color graphics
    """

    modes: ClassVar[dict[str, tuple[str, str]]] = {
      # Name            Code    Description
        "40x24m":       ("0",   "40 x 25 monochrome text"),
        "40x25c":       ("1",   "40 x 25 color text"),
        "80x25m":       ("2",   "80 x 25 monochrome text"),
        "80x25c":       ("3",   "80 x 25 color text"),
        "320x200c4":    ("4",   "320 x 200 4-color graphics"),
        "320x200m":     ("5",   "320 x 200 monochrome graphics"),
        "640X200m":     ("6",   "640 x 200 monochrome graphics"),
        "320x200c":     ("13",  "320 x 200 color graphics"),
        "640x200c":     ("14",  "640 x 200 16-color graphics"),
        "640x350m":     ("15",  "640 x 350 monochrome 2-color graphics"),
        "640x350c":     ("16",  "640 x 350 16-color graphics"),
        "640x480m":     ("17",  "640 x 480 monochrome 2-color graphics"),
        "640x480c":     ("18",  "640 x 480 16-color graphics"),
        "320x200c":     ("19",  "320 x 200 256-color graphics"),
    }

    @classmethod
    def parse(cls, value: str) -> str | None:
        """Parse a screen mode string and return corresponding ANSI value."""
        value = value.lower()
        if value in cls.modes:
            return cls.modes[value][0]
        return None

    # @classmethod
    # def make_mode_list(cls) -> str:
    #     buffer: list[str] = []
    #     for mode_name, mode_values in cls.modes.items():
    #         buffer.append(f'* "{mode_name}": {mode_values[1]}')
    #     return "\n".join(buffer)