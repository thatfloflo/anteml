"""ANSI Terminal Markup Language (AnTeML)."""
import logging
from anteml.parser import AntemlParser

logger = logging.getLogger(__name__)

long_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean felis est, convallis nec euismod vel, imperdiet eu lacus. Nunc quis elementum velit, at tincidunt nulla. Interdum et malesuada fames ac ante ipsum primis in faucibus. Etiam sed viverra sapien. Nullam quis faucibus nisi. Duis mattis iaculis mi, eu viverra nunc fermentum eu. Pellentesque facilisis odio quis erat ultricies, vel convallis tellus dapibus."

test_strings = {
    "Doctype and ANTEML tags":
        """<!DOCTYPE AnTeML "AnTeML.dtd"><anteml>Plain text</anteml>""",
    "Comments":
        """Visible <!-- inside a comment --> Visible""",
    "Foreground color":
        """Normal <fg green>Green <fg blue>Blue <fg yellow>Yellow <fg white>White</fg> Yellow</fg> Blue</fg> Green</fg> Normal""",
    "Background color":
        """Normal <bg green>Green <bg blue>Blue <bg yellow>Yellow <bg white>White</bg> Yellow</bg> Blue</bg> Green</bg> Normal""",
    "256-color decimal background":
        """Normal <bg D10>D10 <bg D50>D50 <bg D100>D100 <bg D150>D150 <bg D255>D255</bg> D150</bg> D100</bg> D50</bg> D10</bg> Normal""",
    "Full color hexadecimal-triplet background":
        """Normal <bg X111>#111 <bg X555>#555 <bg X999>#999 <bg XAAA>#AAA <bg XFFF>XFFF</bg> #AAA</bg> #999</bg> #555</bg> #111</bg> Normal""",
    "Full color hexadecimal background":
        """Normal <bg X0000FF>#0000FF <bg X00FFFF>#00FFFF <bg XFFFFFF>#FFFFFF <bg XFFFF00>#FFFF00 <bg XFF0000>#FF0000 <bg X000000>#000000</bg> #FF0000</bg> #FFFF00</bg> #FFFFFF</bg> #00FFFF</bg> #0000FF</bg> Normal""",
    "Font weight (fw tags)":
        """Normal <fw bold>Bold/bright <fw normal>Normal <fw light>Light/dim/faint <fw bold>Bold/bright</fw> Light/dim/faint</fw> Normal</fw> Bold/bright</fw> Normal""",
    "Font weight (aliases)":
        """Normal <b> Bold/bright <fw normal>Normal <l>Light/dim/faint <b>Bold/bright</b> Light/dim/faint</l> Normal</fw> Bold/bright</b> Normal""",
    "Font styles":
        """Normal <i>Italic <u>Underlined <s>Strikethrough</s> Underlined</u> Italic</i> Normal""",
    "Display mode":
        """Normal <blink>Blinking <invert>Inverted <hide>Hidden</hide> Inverted</invert> Blinking</blink> Normal""",
    # "Screen mode - Line wrapping":
    #     f"""WRAP=ON: <screen wrap=yes>{long_text}<br />
    #         WRAP=OFF: <screen wrap=no>{long_text}</screen><br />
    #         WRAP=ON: {long_text}</screen>""",
    # "Screen mode - Emulate format":
    #     f"""<screen mode=80x25m wrap=off><b>Any difference now?</b><br />{long_text}</screen>""",
}

old_testdoc = """
    <screen mode=SCREEN_MODE>
        Hello World!
        <fg green>Green text, default background</fg>
        <bg yellow>Default text, yellow background</bg>
        Default text, default background
        <bg white><fg black>Black text, white background</fg></bg>
        <br>
        &lt;x&BEL;y&#43;z&gt;
        <br />
    </screen>
    <?proc foo>
"""

logging.basicConfig(level=logging.INFO)
test_buffer: list[str] = []
def test_receiver(data: str):
    test_buffer.append(data)

parser = AntemlParser(receiver=test_receiver, strip_unknown=False)
for test_name, test_string in test_strings.items():
    test_buffer = []
    print(f"\n\n==== {test_name.upper()} ====")
    parser.feed(test_string)
    print("Input:")
    print("  ", test_string.strip("\n"))
    print("Raw output:")
    print("  ", repr("".join(test_buffer)))
    print("Display output:")
    print("  ", "".join(test_buffer), end="\x1b[m\n") # "\x1b[m" should reset everything
