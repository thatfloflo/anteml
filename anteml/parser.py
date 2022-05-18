
"""AnTeML parser implementation."""
import re
import logging
from typing import Callable, Any, Type, ClassVar, Pattern
from html.parser import HTMLParser
from .entities import entities as default_entities
from .elements import Element, ElementAlias, elements as default_elements

__all__ = ["AntemlParser"]

logger = logging.getLogger(__name__)


class AntemlParser(HTMLParser):
    """Standard parser for AnTeML."""

    # Class attributes
    strip_whitespace_patterns: ClassVar[list[tuple[Pattern[str], str]]] = [
        (re.compile(r"\s\s+", re.U),                r" "),
        (re.compile(r"\s(?=\<[^\<]*\>\s)"),         r""),
        (re.compile(r"\A((?:\<[^\<]*\>)*)\s"),      r"\1"),
        (re.compile(r"\s((?:\<[^\<]*\>\s?)*)\Z"),   r"\1"),
    ]  # @TODO: Find a better whitespace stripping pattern/algorithm

    doctype_pattern: ClassVar[Pattern[str]] = re.compile(
        r"\ADOCTYPE\s+AnTeML\s?.*\Z",
        re.IGNORECASE
    )

    # Instance attributes
    element_handlers: dict[str, Element | ElementAlias]
    entities: dict[str, tuple[str, str]]
    options: dict[str, bool]
    receiver: Callable[[str], Any]


    def __init__(
        self,
        receiver: Callable[[str], Any],
        *,
        strip_whitespace: bool = True,
        strip_unknown: bool = False,
        strip_comments: bool = False,
        element_map: dict[str, Type[Element] | Type[ElementAlias]] | None = None,
        entity_map: dict[str, tuple[str, str]] | None = None
    ) -> None:
        """Initialise and reset a new instance of the AnTeML parser."""
        super().__init__(convert_charrefs=False)
        self.receiver = receiver
        self.options = {
            "strip_whitespace": strip_whitespace,
            "strip_unknown": strip_unknown,
            "strip_comments": strip_comments
        }
        self.element_handlers = {}
        if element_map is None:
            element_map = default_elements
        for name, handler in element_map.items():
            self.element_handlers[name] = handler()
        self.entities = {}
        if entity_map is None:
            self.entities = default_entities
        else:
            self.entities = entity_map


    def feed(self, data: str, strip_whitespace: bool | None = None) -> None:
        if strip_whitespace is None:
            strip_whitespace = self.options["strip_whitespace"]
        if strip_whitespace:
            return super().feed(self.strip_whitespace(data))
        return super().feed(data)


    def handle_charref(self, name: str) -> None:
        if name.startswith("x"):
            char = chr(int(name[1:], 16))
        else:
            char = chr(int(name))
        logger.debug(f"CHARREF: {char}")
        self.output(char)


    def handle_comment(self, data: str) -> None:
        logger.debug(f"COMMENT: {data}")
        if not self.options["strip_comments"]:
            self.output(f"<!-- {data} -->")


    def handle_data(self, data: str) -> None:
        logger.debug("DATA: {data}")
        self.output(data)


    def handle_decl(self, decl: str) -> None:
        logger.debug(f"DECLARATION: {decl}")
        if not self.doctype_pattern.match(decl) and not self.options["strip_unknown"]:
            self.output(f"<!{decl}>")


    def resolve_endtag_alias(
        self,
        tag: str,
    ) -> str:
        if tag in self.element_handlers:
            handler = self.element_handlers[tag]
            if isinstance(handler, ElementAlias):
                element_type = handler.end()
                logger.debug(f"REWRITING ENDTAG ALIAS: {tag} -> {element_type.tag}")
                tag = element_type.tag
        return tag


    def resolve_starttag_alias(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]]
    ) -> tuple[str, list[tuple[str, str | None]]]:
        if tag in self.element_handlers:
            handler = self.element_handlers[tag]
            if isinstance(handler, ElementAlias):
                element_type, element_attrs = handler.start(attrs)
                logger.debug(f"REWRITING ENDTAG ALIAS: {tag} (ATTRS: {attrs}) -> {element_type.tag} (ATTRS: {element_attrs})")
                tag = element_type.tag
                attrs = element_attrs
        return (tag, attrs)


    def handle_endtag(self, tag: str) -> None:
        orig_tag = tag
        tag = self.resolve_endtag_alias(tag.lower())
        if tag in self.element_handlers:
            handler = self.element_handlers[tag]
            if not isinstance(handler, Element):
                logger.critical(f"Encountered invalid element handler {handler!r} for tag {tag!r}")
                return
            logger.debug(f"ENDTAG: {tag}")
            v = handler.end()
            logger.debug(f"ENDTAG VALUE: {v!r}")
            self.output(v)
        else:
            logger.warning(f"UNKNOWN ENDTAG: {tag}")
            if not self.options["strip_unknown"]:
                self.output(f"</{orig_tag}>")                           # type: ignore


    def handle_entityref(self, name: str) -> None:
        if name in self.entities:
            value = self.entities[name][0];
            logger.debug(f"ENTITYREF: {name!r} -> {value!r}")
        elif not self.options["strip_unknown"]:
            value = f"&{name};"
            logger.debug(f"UNKNOWN ENTITYREF: {name!r} -> {value!r}")
        else:
            logger.warning(f"UNRESOLVABLE ENTITYREF: {name!r}")
            value = ""
        self.output(value)


    def handle_pi(self, data: str) -> None:
        # @ TODO: IMPLEMENT
        logger.debug(f"PROCESSING INSTRUCTION: {data}")
        logger.error("PROCESSING INSTRUCTIONS NOT IMPLEMENTED YET")


    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag, attrs = self.resolve_starttag_alias(tag.lower(), attrs)
        if tag not in self.element_handlers:
            logger.warning(f"UNKNOWN STARTENDTAG: {tag} (ATTRS: {attrs})")
            if not self.options["strip_unknown"]:
                self.output(self.get_starttag_text())  # type: ignore
            return
        
        handler = self.element_handlers[tag]
        if not isinstance(handler, Element):
            logger.critical(f"Encountered invalid element handler {handler!r} for tag {tag!r}")
            return

        logger.debug(f"STARTENDTAG: {tag} (ATTRS: {attrs})")
        v = handler.start(attrs) + handler.end()
        logger.debug(f"STARTENDTAG VALUE: {v!r}")
        self.output(v)


    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag, attrs = self.resolve_starttag_alias(tag.lower(), attrs)
        if tag not in self.element_handlers:
            logger.warning(f"UNKNOWN STARTTAG: {tag} (ATTRS: {attrs})")
            if not self.options["strip_unknown"]:
                self.output(self.get_starttag_text())  # type: ignore
            return

        handler = self.element_handlers[tag]
        if not isinstance(handler, Element):
            logger.critical(f"Encountered invalid element handler {handler!r} for tag {tag!r}")
            return

        logger.debug(f"STARTTAG: {tag} (ATTRS: {attrs})")
        v = handler.start(attrs)
        logger.debug(f"STARTTAG VALUE: {v!r}")
        self.output(v)


    def output(self, data: str) -> None:
        """Pass output to the parser's receiver."""
        self.receiver(data)


    def set_receiver(self, receiver: Callable[[str], Any]) -> None:
        """Set the receiver for data processed by the parser."""
        self.receiver = receiver


    def strip_whitespace(self, data: str) -> str:
        """Remove redundant whitespace from AnTeML code."""
        for pattern, repl in self.strip_whitespace_patterns:
            data = pattern.sub(repl, data)
        return data


    def unknown_decl(self, data: str) -> None:
        """Handle unknown declarations."""
        logger.warning(f"UNKNOWN_DECLARATION: {data}")
        super().unknown_decl(data)