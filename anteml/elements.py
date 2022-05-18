import logging
from abc import ABC, abstractmethod
from typing import ClassVar, Final, Type
from textwrap import wrap
from .errors import AntemlAttributeError
from .attributes import Color, FontWeight, ScreenMode, Boolean

__all__ = ["Element", "ElementAlias", "AntemlElement", "FgElement", "elements"]

logger = logging.getLogger(__name__)

class Element(ABC):
    """Abstract base class for AnTeML Elements.
    
    All AnTeML Element handler are derived from this class. Note that unlike in
    a common DOM model, individual pairs of SGML element tags are not
    represented by an individual instance of the related Element class, rather
    the related Element class represents a stack keeping track of the state of
    all instances of use of this tag in the SGML document.

    On the one hand, this aligns more easily with how the underlying parser
    (`HTMLParser` from the `html.parsing` package) works, on the other hand it
    facilitates stream-based parsing and presentation of AnTeML content, where
    a tag might be opened long before it is known when (or whether) it will be
    closed to revert to the previous state.

    By default, the behaviour of an Element handler is as follows:
    * The handler's class attributes `tag` and `default` provide static
        information about the the Element (associated tag, default-value ANSI
        code). This should normally be treated as `typing.Final` in derived
        classes.
    * The handler is instantiated by the parser either on parser-initialisation
        or when the associated tag is encountered for the first time, and a
        reference is held by the parser for the parsers' lifetime.
    * When the associated opening tag is encountered, the element handler's
        `start()` method is called by the parser.
        For most element types, the `start()` method does the following:
        - On the first call, this will push the element's `default` value onto
            the element handler's `stack` and set the element handler's `state`
            to the value associated with the state encoded in the tag (and its
            tuple of attrs, if any).
        - On subsequent calls, the current `state` is pushed onto the `stack`
            before setting the active `state` to the value associated with the
            state encoded in the tag (and its tuple of attrs, if any).
        - Finally, the ANSI code needed to present the current state is
            returned.
    * When the associated closing tag is encountered, the element handler's
        `end()` method is called by the parser.
        For most element types, the `end()` method does the following:
        - Pop the last state from the element handler's `stack` and set the
            current `state` to its value.
        - Return the ANSI code needed to present the current state.
    """

    # Class attributes
    tag: ClassVar[str] = ""
    default: ClassVar[str] = ""

    # Instance attributes
    stack: list[str]
    state: str | None

    def __init__(self):
        """Initialise a handler for instances of the element type."""
        self.stack = []
        self.state = None

    def push_state(self, state: str) -> str:
        """Push the current `state` onto the stack and set current `state` to *state*."""
        if self.state is not None:
            self.stack.append(self.state)
        else:
            self.stack.append(self.default)
        self.state = state
        return state

    def pop_state(self) -> str:
        """Pop *state* from the `stack`, set current `state` to *state* and return *state*."""
        try:
            state = self.stack.pop()
        except IndexError:
            state = self.default
        self.state = state
        return state

    @abstractmethod
    def start(self, attrs: list[tuple[str, str | None]]) -> str:
        """Initialise an element: called when the associated tag is opened."""
        ...

    @abstractmethod
    def end(self) -> str:
        """Destruct an element: called when the associated tag is closed."""
        ...


class AntemlElement(Element):
    """Handler for the optional ANTEML element.
    
    AnTeML may optionally be enclosed by `<ANTEML>...</ANTEML>` tags. In current
    implementations these have no effect whatever, and purely serve as
    facilitators for the inclusion or identification of AnTeML content inside
    other document content on the user's side.
    """

    # Class attributes
    tag: Final[str] = "anteml"
    default: Final[str] = ""

    def start(self, attrs: list[tuple[str, str | None]]) -> str:
        """Initialise an AntemlElement instance when the associated tag is opened.

        This does nothing at all and always returns an empty string, because
        `<ANTEML>...</ANTEML>` have no associated presentation or parsing behaviour.
        """
        return ""

    def end(self) -> str:
        """Destruct an AntemlElement instance when the associated tag is closed.

        This does nothing at all and always returns an empty string, because
        `<ANTEML>...</ANTEML>` have no associated presentation or parsing behaviour.
        """
        return ""


class BrElement(Element):
    """Handler for the BR (break row) element.

    The break row element inserts a new line in the output, similar to HTML
    `<br>`. The BR element accepts no attribute, and the closing tag is optional
    (typical usage will be as a sole opening tag `<br>` or a XML-style self-closed
    tag `<br />`).
    """

    # Class attributes
    tag: Final[str] = "br"
    default: Final[str] = "\n"

    def start(self, attrs: list[tuple[str, str | None]]) -> str:
        if len(attrs) > 0:
            raise AntemlAttributeError(f"<BR> tag does not accept attributes (0 expected, {len(attrs)} given)")
        return self.default

    def end(self) -> str:
        return ""


class FwElement(Element):
    """Handler for the Fw (font weight) element.
    
    The font weight elemenent sets the terminal text to bold/bright, normal, or
    light/dim/faint. The exact realisation depends on the implementation of the
    terminal.

    The FW element expects exactly 1 attribute, a FontWeight, which may be one
    of the literals "BOLD", "NORMAL", or "LIGHT".

    Example:
        `Hello <FW BOLD>World</FW>! What is your <FW BOLD>name</FW>?`

        This will produce the text "Hello **World**! What is your **name**?" with
        the words "World" and "name" in boldface or brighter highlight (depending
        on the terminal used).
    """

    # Class attributes
    tag: Final[str] = "fw"
    default: Final[str] = "\x1b[22m"

    def start(self, attrs: list[tuple[str, str | None]]) -> str:
        """Initialise a FwElement instance when the associated tag is opened."""
        if len(attrs) != 1:
            raise AntemlAttributeError(f"<FW> tag has the incorrect number of attributes (exactly 1 expected, {len(attrs)} given)")
        if fw := FontWeight.parse(attrs[0][0]):
            code = self.default + f"\x1b[{fw}m"
            return self.push_state(code)
        else:
            raise AntemlAttributeError(f"Invalid #FONTWEIGHT attribute '{attrs[0][0]}' on <FW> tag")

    def end(self) -> str:
        """Destruct a FwElement instance when the associated tag is closed. """
        return self.pop_state()


class BgElement(Element):
    """Handler for the BG (background) element.
    
    The background elemenent sets the background color of the terminal text. The
    BG element acceepts one bare attribute value of type `#COLOR`.

    Example:
        `Hello <BG YELLOW>World</BG>! What is your <BG GREEN>name</BG>?`

        This will set the background color of "World" to yellow (ANSI background
        color `43`), then reset it to the default (ANSI background color
        `49`), then set the background color of "name" to green (ANSI background
        color `42`) before resetting it back to the default (ANSI background
        color `49`) preceding the question mark.

    Example:
        `<BG X333>Do you like reading <BG X4169E1>Royal Blue</BG> text?</BG>`

        This will initially set the background color to dark grey (hex
        color #333333). The background will then be set to royal blue (hex color
        #4169E1) before "Royal", and revert to dark grey (hex color #333333)
        following "Blue". At the end of the string, the color will be reset to
        the default (ANSI background color `49`).
    """

    # Class attributes
    tag: Final[str] = "bg"
    default: Final[str] = "\x1b[49m"

    def start(self, attrs: list[tuple[str, str | None]]) -> str:
        """Initialise a BgElement instance when the associated tag is opened."""
        if len(attrs) != 1:
            raise AntemlAttributeError(f"<BG> tag has the incorrect number of attributes (exactly 1 expected, {len(attrs)} given)")
        if color_attr := Color.parse(attrs[0][0]):
            color_t, color_bg = color_attr[0], color_attr[2]
            code: str = ""
            if color_t == "name":
                code = f"\x1b[{color_bg}m"
            elif color_t == "decimal":
                code = f"\x1b[48;5;{color_bg}m"
            elif color_t == "hex":
                r, g, b = [int(c, 16) for c in wrap(color_bg, 2)]
                code = f"\x1b[48;2;{r};{g};{b}m"
            return self.push_state(code)
        else:
            raise AntemlAttributeError(f"Invalid #COLOR attribute '{attrs[0][0]}' on <BG> tag")

    def end(self) -> str:
        """Destruct a BgElement instance when the associated tag is closed. """
        return self.pop_state()


class FgElement(Element):
    """Handler for the FG (foreground) element.
    
    The foreground elemenent sets the foreground color of the terminal text. The
    FG element acceepts one bare attribute value of type `#COLOR`.

    Example:
        `Hello <FG YELLOW>World</FG>! What is your <FG GREEN>name</FG>?`

        This will set the color to yellow (ANSI foreground color `33`) before
        the text "World", then reset it to the default (ANSI foreground color
        `39`) before the exclamation mark, before setting the foreground color
        to green (ANSI foreground color `32`) before the text "name" and
        resetting it back to the default (ANSI foreground color `39`) preceding
        the question mark.

    Example:
        `<FG X333>Do you like reading <FG X4169E1>Royal Blue</FG> text?</FG>`

        This will initially set the text foreground color to dark grey (hex
        color #333333). The color will then be set to royal blue (hex color
        #4169E1) before "Royal", and revert to dark grey (hex color #333333)
        following "Blue". At the end of the string, the color will be reset to
        the default (ANSI foreground color `39`).
    """

    # Class attributes
    tag: Final[str] = "fg"
    default: Final[str] = "\x1b[39m"

    def start(self, attrs: list[tuple[str, str | None]]) -> str:
        """Initialise an FgElement instance when the associated tag is opened."""
        if len(attrs) != 1:
            raise AntemlAttributeError(f"<FG> tag has the incorrect number of attributes (exactly 1 expected, {len(attrs)} given)")
        if color_attr := Color.parse(attrs[0][0]):
            color_t, color_fg = color_attr[0:2]
            code: str = ""
            if color_t == "name":
                code = f"\x1b[{color_fg}m"
            elif color_t == "decimal":
                code = f"\x1b[38;5;{color_fg}m"
            elif color_t == "hex":
                r, g, b = wrap(color_fg, 2)
                code = f"\x1b[38;2;{r};{g};{b}m"
            return self.push_state(code)
        else:
            raise AntemlAttributeError(f"Invalid #COLOR attribute '{attrs[0][0]}' on <FG> tag")

    def end(self) -> str:
        """Destruct an FgElement instance when the associated tag is closed."""
        return self.pop_state()


class IElement(Element):
    """Handler for the I (italic) element.
    
    The italic elemenent sets the terminal text to italic. The I element accepts
    no attributes.

    Example:
        `Hello <I>World</I>!`

        This will produce the text "Hello *World*!" with
        the words "World" set in italic.
    """

    # Class attributes
    tag: Final[str] = "i"
    default: Final[str] = "\x1b[23m"

    def start(self, attrs: list[tuple[str, str | None]]) -> str:
        """Initialise an IElement instance when the associated tag is opened."""
        if len(attrs) > 0:
            raise AntemlAttributeError(f"<I> tag does not accept attributes (0 expected, {len(attrs)} given)")
        code = f"\x1b[3m"
        return self.push_state(code)

    def end(self) -> str:
        """Destruct a IElement instance when the associated tag is closed."""
        return self.pop_state()


class UElement(Element):
    """Handler for the U (underline) element.
    
    The underline elemenent sets the terminal text to underlined. The U element
    accepts no attributes.

    Example:
        `Hello <U>World</U>!`

        This will produce the text "Hello __World__!" with
        the word "World" set underlined.
    """

    # Class attributes
    tag: Final[str] = "u"
    default: Final[str] = "\x1b[24m"

    def start(self, attrs: list[tuple[str, str | None]]) -> str:
        """Initialise an UElement instance when the associated tag is opened."""
        if len(attrs) > 0:
            raise AntemlAttributeError(f"<U> tag does not accept attributes (0 expected, {len(attrs)} given)")
        code = f"\x1b[4m"
        return self.push_state(code)

    def end(self) -> str:
        """Destruct a UElement instance when the associated tag is closed."""
        return self.pop_state()


class SElement(Element):
    """Handler for the S (strikethrough) element.
    
    The strikethrough elemenent sets the terminal text to stikethrough. The S
    element accepts no attributes.

    Example:
        `Hello <S>World</S>!`

        This will produce the text "Hello <s>World</s>!" with
        the word "World" struck through.
    """

    # Class attributes
    tag: Final[str] = "s"
    default: Final[str] = "\x1b[29m"

    def start(self, attrs: list[tuple[str, str | None]]) -> str:
        """Initialise an SElement instance when the associated tag is opened."""
        if len(attrs) > 0:
            raise AntemlAttributeError(f"<S> tag does not accept attributes (0 expected, {len(attrs)} given)")
        code = f"\x1b[9m"
        return self.push_state(code)

    def end(self) -> str:
        """Destruct a SElement instance when the associated tag is closed."""
        return self.pop_state()


class BlinkElement(Element):
    """Handler for the BLINK element.
    
    The BLINK elemenent sets the terminal text to blinking mode. The BLINK
    element accepts no attributes.

    Example:
        `Hello <BLINK>World</BLINK>!`

        This will produce the text "Hello <blink>World</blink>!" with
        the word "World" blinking.
    """

    # Class attributes
    tag: Final[str] = "blink"
    default: Final[str] = "\x1b[25m"

    def start(self, attrs: list[tuple[str, str | None]]) -> str:
        """Initialise an BlinkElement instance when the associated tag is opened."""
        if len(attrs) > 0:
            raise AntemlAttributeError(f"<BLINK> tag does not accept attributes (0 expected, {len(attrs)} given)")
        code = f"\x1b[5m"
        return self.push_state(code)

    def end(self) -> str:
        """Destruct a BlinkElement instance when the associated tag is closed."""
        return self.pop_state()


class InvertElement(Element):
    """Handler for the INVERT element.
    
    The INVERT elemenent sets the terminal text to inverted/inverse display mode
    (foreground and background color swapped). The INVERT element accepts no
    attributes.

    Example:
        `Hello <INVERT>World</INVERT>!`

        This will produce the text "Hello World!" with the word "World" using
        the inverted display mode to the rest of the terminal text.
    """

    # Class attributes
    tag: Final[str] = "invert"
    default: Final[str] = "\x1b[27m"

    def start(self, attrs: list[tuple[str, str | None]]) -> str:
        """Initialise an InvertElement instance when the associated tag is opened."""
        if len(attrs) > 0:
            raise AntemlAttributeError(f"<INVERT> tag does not accept attributes (0 expected, {len(attrs)} given)")
        code = f"\x1b[7m"
        return self.push_state(code)

    def end(self) -> str:
        """Destruct a InvertElement instance when the associated tag is closed."""
        return self.pop_state()


class HideElement(Element):
    """Handler for the HIDE element.
    
    The HIDE elemenent sets the terminal text to hidden display mode, often
    realised as barely visible text depending on the terminal. The HIDE element
    accepts no attributes.

    Example:
        `Hello <HIDE>World</HIDE>!`

        This will produce the text "Hello World!" with the word "World" using
        the hidden display mode, and either not or barely visible but still
        using up the space it normally would.
    """

    # Class attributes
    tag: Final[str] = "hide"
    default: Final[str] = "\x1b[28m"

    def start(self, attrs: list[tuple[str, str | None]]) -> str:
        """Initialise a HideElement instance when the associated tag is opened."""
        if len(attrs) > 0:
            raise AntemlAttributeError(f"<HIDE> tag does not accept attributes (0 expected, {len(attrs)} given)")
        code = f"\x1b[8m"
        return self.push_state(code)

    def end(self) -> str:
        """Destruct a HideElement instance when the associated tag is closed."""
        return self.pop_state()


class ScreenElement(Element):
    """Handler for the SCREEN element.
    
    The SCREEN element sets the terminal emulation mode and/or text-wrapping
    mode.
    
    SCREEN accepts two optional attributes:
    * MODE=#SCREENMODE - See `attributes.ScreenMode` for possible values.
    * WRAP=#BOOL - Whether linewrapping should be used or not, boolean value
        may be indicated by a truthy value like "1", "on", "yes", "true" or a
        falsy value like "0", "off", "no", "false".
    """

    # Class attributes
    tag: Final[str] = "screen"
    default: Final[str] = "\x1b7h"

    def _determine_screen_mode(self, value: str | None) -> str:
        if value is None:
            raise AntemlAttributeError(f"Attribute 'MODE' specified without value on <SCREEN> tag")
        v = ScreenMode.parse(value)
        if v is None:
            raise AntemlAttributeError(f"Invalide value {value!r} for 'MODE' attribute on <SCREEN> tag")
        return v

    def _determine_line_wrap(self, value: str | None) -> bool:
        if value is None:
            raise AntemlAttributeError(f"Attribute 'WRAP' specified without value on <SCREEN> tag")
        v = Boolean.parse(value)
        if v is None:
            raise AntemlAttributeError(f"Invalide value {value!r} for 'WRAP' attribute on <SCREEN> tag")
        return v

    def start(self, attrs: list[tuple[str, str | None]]) -> str:
        """Initialise a ScreenElement instance when the associated tag is opened."""
        if len(attrs) > 2:
            raise AntemlAttributeError(f"<SCREEN> tag has too many attributes (max. 2 expected, {len(attrs)} given)")
        screen_mode: str | None = None
        line_wrap: bool | None = None
        for attr_name, attr_value in attrs:
            attr_name = attr_name.lower()
            if attr_name == "mode":
                if screen_mode is not None:
                    raise AntemlAttributeError(f"Attribute 'MODE' specified more than once on <SCREEN> tag")
                screen_mode = self._determine_screen_mode(attr_value)
            if attr_name == "wrap":
                if line_wrap is not None:
                    raise AntemlAttributeError(f"Attribute 'WRAP' specified more than once on <SCREEN> tag")
                line_wrap = self._determine_line_wrap(attr_value)
        start_code: str = ""
        end_code: str = ""
        if screen_mode is not None:
            start_code += f"\x1b[={screen_mode}h"
        if line_wrap is True:
            start_code += "\x1b[=7h"
            end_code += "\x1b[=7h"  # Assume line wrapping is on by default
        if line_wrap is False:
            start_code += "\x1b[=7l"
            end_code += "\x1b[=7h"
        if screen_mode is not None:
            end_code += f"\x1b[={screen_mode}l"

        self.push_state(end_code)
        return start_code

    def end(self) -> str:
        """Destruct a HideElement instance when the associated tag is closed."""
        return self.pop_state()


class ElementAlias(ABC):
    """Abstract base class for Alias Elements.
    
    An `ElementAlias` looks and behaves somewhat similarly to a regular `Element`,
    however, they are really aliases for another `Element`. The crucial
    difference is than the `start()` and `end()` methods of an `ElementAlias`
    don't return the ANSI presentation code associated with an `Element`/tag,
    but rather they return a different AnTeML tag with which the original
    occurence of the `ElementAlias`'s tags are to be overwritten.
    """

    # Class attributes
    tag: ClassVar[str] = ""
    resolves_to: ClassVar[Type[Element]] = Element

    @abstractmethod
    def start(self, attrs: list[tuple[str, str | None]]) -> tuple[Type[Element], list[tuple[str, str | None]]]:
        """Returns AnTeML markup to rewrite the `ElementAlias` start tag."""
        return (self.resolves_to, attrs)

    @abstractmethod
    def end(self) -> Type[Element]:
        """Returns AnTeML markup to rewrite the `ElementAlias` end tag."""
        return self.resolves_to


class BElementAlias(ElementAlias):
    """An element alias for bold/bright text.
    
    The B element is an alias for the `FwElement` with the `FontWeight`
    attribute set to `bold`. That is, `<B>Hello!</B>` is equivalent to
    `<FW BOLD>Hello!</FW>` and will get rewritten as such.
    """

    # Class attributes
    tag: Final[str] = "b"
    resolves_to: Final[Type[Element]] = FwElement

    def start(self, attrs: list[tuple[str, str | None]]) -> tuple[Type[Element], list[tuple[str, str | None]]]:
        if len(attrs) > 0:
            raise AntemlAttributeError(f"<B> tag does not accept attributes (0 expected, {len(attrs)} given)")
        return (self.resolves_to, [("bold", None)])

    def end(self) -> Type[Element]:
        return self.resolves_to


class LElementAlias(ElementAlias):
    """An element alias for light/dim/faint text.
    
    The L element is an alias for the `FwElement` with the `FontWeight`
    attribute set to `light`. That is, `<L>Hello!</L>` is equivalent to
    `<FW LIGHT>Hello!</FW>` and will get rewritten as such.
    """

    # Class attributes
    tag: Final[str] = "l"
    resolves_to: Final[Type[Element]] = FwElement

    def start(self, attrs: list[tuple[str, str | None]]) -> tuple[Type[Element], list[tuple[str, str | None]]]:
        if len(attrs) > 0:
            raise AntemlAttributeError(f"<L> tag does not accept attributes (0 expected, {len(attrs)} given)")
        return (self.resolves_to, [("light", None)])

    def end(self) -> Type[Element]:
        return self.resolves_to


elements: dict[str, Type[Element] | Type[ElementAlias]] = {
    # Core elements
    "anteml": AntemlElement,
    "br": BrElement,
    "bg": BgElement,
    "fg": FgElement,
    "fw": FwElement,
    "i": IElement,
    "u": UElement,
    "s": SElement,
    "blink": BlinkElement,
    "hide": HideElement,
    "invert": InvertElement,
    "screen": ScreenElement,
    # Alias elements
    "b": BElementAlias,
    "l": LElementAlias,
}