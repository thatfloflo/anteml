from anteml.parser import AntemlParser
import re
import sys
from typing import Pattern

version: str = "1.0.0"
name_pattern: Pattern[str] = re.compile(
    r"\A\w[\w ]+\w\Z",
    re.UNICODE
)
p = AntemlParser(lambda x: print(x, end="", flush=True))

p.feed(
    "<BG WHITE><FG BLACK>Welcome to the <B><FG RED>People Greeter</FG></B> "
    f"<L>(version {version})</L>!</FG></BG><BR><BR>"
)
p.feed("Please type your name: <L><FG x999>(confirm with Enter)</FG></L><BR>")

while True:
    p.feed("<I>")
    name = input().strip()
    p.feed("</I>")
    if name_pattern.fullmatch(name):
        break
    p.feed(
        f"<L><FG RED>Oops, the string <I>{name!r}</I> doesn't look like a valid"
        " name...</FG><BR>"
        "<FG x999>A name should be at least 2 characters and consist only of "
        "unicode word characters and spaces.</FG></L><BR>"
        "Please try again:<BR>"
    )

p.feed(
    f"<BR><B>Welcome, <INVERT><BLINK>{name}</BLINK></INVERT>!<BR>"
    "<FG GREEN>Be greeted!</FG></B>"
)
sys.exit(0)