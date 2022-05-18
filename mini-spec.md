# Draft notes for an AnTeML mini-language specification

### Disclaimer:

This is a loose and fast draft, more intended as some notes showing the original idea for the mini-language. It is neither guaranteed to be a good reference for the mini-language, nor correct, nor in sync with
the source or other files.

Eventually, when the implementation is more complete and stable a definitive DTD should be written and documentation based on this.

For a current and up-to-date reference of what's possible/implemented so far, it's best to inspect the source and examples (or generate API reference documentation from it with Sphix or the like - the source is relatively well documented).

## Entities

***Note***: As opposed virtually everything else in AnTeML, entity names ***are* case-sensitive**. This means that `&ABC;` and `&abc;` are *not* the same, and in most cases the equivalent sequence with the other case
simply does not exist.

### Control sequences

#### Escape control sequences

| Entity    | Value             | Description                 |
| --------- | ----------------- | --------------------------- |
| `&ESC;`   | 0x1B              | Escape character            |
| `&CSI;`   | 0x9B ~ `&ESC;[`   | Control Sequence Introducer |
| `&DCS;`   | 0x90 ~ `&ESC;P`   | Device Control String       |
| `&OSC;`   | 0x9D ~ `&ESC;]`   | Operating System Command    |

#### Message control sequences

| Entity    | Value             | Description                 |
| --------- | ----------------- | --------------------------- |
| `&ST;`    | 0x9C              | String Terminator           |
| `&SOS;`   | 0x98              | Start of string             |
| `&PM;`    | 0x9E              | Privacy message             |
| `&APC;`   | 0x9F              | Application Program Command |

#### Other control sequences

| Entity    | Value             | Description                 |
| --------- | ----------------- | --------------------------- |
| `&BEL;`   | 0x07              | Terminal bell               |
| `&BS;`    | 0x08              | Backspace                   |
| `&HT;`    | 0x09              | Horizontal tab              |
| `&LF;`    | 0x0A              | Linefeed                    |
| `&VT;`    | 0x0B              | Vertical tab                |
| `&FF;`    | 0x0C              | Form feed                   |
| `&CR;`    | 0x0D              | Carriage return             |
| `&DEL;`   | 0x7F              | Delete character            |

### Other symbols

#### General (not all implemented yet)

**Note**: The below list is currently attempting to draft a somewhat more consistent naming scheme than found in HTML entities. However, given established familiarity with HTML entities and potential for confusion, it might be better to simply adopt the standard HTML entities (or a subset of those). Alternatively there could be some "more consistent aliases" (but that probably makes it even worse, if anything - no need for the bloat).

| Entity    | Value             | Description                 |
| --------- | ----------------- | --------------------------- |
| `&amp;`   | &amp;             | Ampersand                   |
| `&squo;`  | '                 | Single block quote          |
| `&lsquo;` | &lsquo;           | Left single quote           |
| `&rsquo;` | &rsquo;           | Right single quote          |
| `&bsquo;` | &sbquo;           | Low (bottom) single quote   |
| `&dquo;`  | &quot;            | Double block quote          |
| `&ldquo;` | &ldquo;           | Left double quote           |
| `&rdquo;` | &rdquo;           | Right double quote          |
| `&bdquo;` | &bdquo;           | Low (bottom) double quote   |

#### Unicode character reference

As in HTML/XML, characters can be referenced by their unicode character codes, either as ordinal with `&#N;` (where *N* is a decimal number) or as a hexadecimal with `&#xN;` (where *N* is a hexadecimal number).


## Attribute value types

**Note:** Attribute value types (except #PCDATA) are generally case-insensitive, i.e. `MAGENTA` and `magenta` are treated as equivalent.

### #COLOR:
 - One of the literals "BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", or "WHITE".
 - Literal "D" followed by a decimal number between 0 and 255, e.g. "D0", "D28", "D255".
 - Literal "X" followed by hex triplet for RGB values as either RGB or RRGGBB, e.g. "X333" (=0x333333) or "XA03F22" (=0xA03F22)

### #RAWSEQ:
 - A raw escape sequence string, consisint of characters [0-9a-Z\[\];]

### #NUM:
 - Any decimal integer preceded by D, e.g. "D0", "D7", ...
 - Any hexadecimal integer, preceded by X, e.g. "X027DF"

### #BOOLEAN:
 - One of the literals "on", "off", "true", "false", "0", "1", "yes", "no"

### #FONTWEIGHT:
 - One of the literals "BOLD", "NORMAL", "LIGHT".

### #SCREENMODE:
 - A #NUM between (decimal) 0-6 or 13 to 19
 - One of the literals:
	 0. 40X24-MONO		40 x 25   monochrome	text
	 1. 40X25-COLOR		40 x 25	  color		text
	 2. 80x25-MONO		80 x 25	  monochrome	text
	 3. 80X25-COLOR		80 x 25	  color		text
	 4. 320X200-4COLOR	320 x 200 4-color	graphics
	 5. 320X200-MONO	320 x 200 monochrome	graphics
	 6. 640X200-MONO	640 x 200 monochrome	graphics
	13. 320X200-COLOR	320 x 200 color		graphics
	14. 640x200-COLOR	640 x 200 color		16-color graphics 
	15. 640X350-MONO	640 x 350 monochrome	2-color graphics
	16. 640x350-COLOR	640 x 350 color		16-color graphics
	17. 640X480-MONO	640 x 480 monochrome	2-color graphics
	18. 640X480-COLOR	640 x 480 color		16-color graphics
	19. 320X200-COLOR	320 x 200 color		256-color graphics		

### #PCDATA
 - Any string data not containing the bare special characters "&lt;", "&gt;" or "&amp;".

## Elements

**Note:** Element tags are case-insensitive, i.e. `<Foo>`, `<fOO>`, `<FOO>`, `<foo>` etc. are all treated the same. 

### ANTEML Document Delimiters

#### AntemlElement
* **Description:** Optional document delimiters.
* **Attributes:**
	- *None.*
* **Example:** `<ANTEML>#PCDATA</ANTEML>`				

### Screen display mode

#### ScreenElement
* **Description:** Sets screen display and line wrapping mode.
* **Attributes**:
	- *MODE*: #SCREENMODE, the screen display emulation mode.
	- *WRAP*: #BOOLEAN, turn line-wrapping on or off.
* **Example:** `<SCREEN MODE=#SCREEN-MODE WRAP=#BOOLEAN>#PCDATA</SCREEN>`

### Colors

#### FgElement
* **Description:** Sets the foreground color.
* **Attributes:**
 	- Accepts a bare #COLOR reference as an attribute, which sets the foreground color value.  
 	*Note*: If color is a color name, this will be treated as an 8-color system reference. If it is a decimal number between 0-255 it will be treated as a 256-color system reference, and if it is a hexadecimal (either as RGB or RRGGBB) it will be treated as a full-color reference.
* **Example:** `<FG #COLOR>#PCDATA</FG>`

#### BgElement
* **Description:** Sets the background color.
* **Attributes:**
 	- Accepts a bare #COLOR reference as an attribute, which sets the background color value.  
 	*Note:* If color is a color name, this will be treated as an 8-color system reference. If it is a decimal number between 0-255 it will be treated as a 256-color system reference, and if it is a hexadecimal (either as RGB or RRGGBB) it will be treated as a full-color reference.
* **Example:** `<BG #COLOR>#PCDATA</BG>`

### Font weight

#### FwElement
* **Description:** Sets the font weight.
* **Attributes:**
	- Accepts a bare #FONTWEIGHT reference as an attribute, which indicates the font weight or brightness level to be used (implementation dependent on the display terminal).
* **Example:**: `<FW #FONTWEIGHT></FW>`

#### BElement (alias for FwElement)
* **Description:** Sets the font weight to *bold* (aka *bright*). This is an alias for `<FW BOLD>...</FW>`.
* **Attributes:**
	- *None.*
* **Example:**: `<B>#PCDATA</B>`

#### LElement (alias for FwElement)
* **Description:** Sets the font weight to *light* (aka *dim* or *faint*). This is an alias for `<FW LIGHT>...</FW>`.
* **Attributes:**
	- *None.*
* **Example:**: `<L>#PCDATA</L>`

### Text decoration

#### IElement
* **Description:** Sets the text mode to *italic*.
* **Attributes:**
	- *None.*
* **Example:**: `<I>#PCDATA</I>`

#### UElement
* **Description:** Sets the text mode to <u>underlined</u>.
* **Attributes:**
	- *None.*
* **Example:**: `<U>#PCDATA</U>`

#### BlinkElement
* **Description:** Sets the text mode to *blinking*.
* **Attributes:**
	- *None.*
* **Example:**: `<BLINK>#PCDATA</BLINK>`

#### InvertElement
* **Description:** Sets the text mode to *inverted* (aka *inverse*), with the foreground and background colors swapped.
* **Attributes:**
	- *None.*
* **Example:**: `<INVERT>#PCDATA</INVERT>`

#### HideElement
* **Description:** Sets the text mode to *hidden* (aka *concealed* or *invisible*). Depending on the terminal this is typically either realised as very low contrast text or as text with the foreground color set to match the background color.
* **Attributes:**
	- *None.*
* **Example:**: `<HIDE>#PCDATA</HIDE>`

#### SElement
* **Description:** Sets the text mode to <strike>strikethrough</strike> (aka *strikeout*).
* **Attributes:**
	- *None.*
* **Example:**: `<S>#PCDATA</S>`

## Processing instructions (not implemented yet)

### Escape sequences

| Code example     | Description                |
| ---------------- | -------------------------- |
| `<?ESC #RAWSEQ>` | Same as `&ESC;#RAWSEQ`     |
| `<?CSI #RAWSEQ>` | Same as `&CSI;#RAWSEQ`     |
| `<?DCS #RAWSEQ>` | Same as `&DCS;#RAWSEQ&ST;` |
| `<?OSC #RAWSEQ>` | Same as `&OSC;#RAWSEQ&ST;` |

### Cursor control

| Code example             | Description                                           |
| ------------------------ | ----------------------------------------------------- |
| `<?C UP=#NUM>`           | Move cursor up NUM lines                              |
| `<?C DOWN=#NUM>`         | Move cursor down NUM lines                            |
| `<?C FORWARD=#NUM>`      | Move cursor right NUM columns                         |
| `<?C BACK=#NUM>`         | Move cursor left NUM columns                          |
| `<?C NEXTLN=#NUM>`       | Move cursor to beginning of next line, # lines down   |
| `<?C PREVLN=#NUM>`       | Move cursor to beginning of previous line, # lines up |
| `<?C COL=#NUM>`          | Move cursor to column NUM                             |
| `<?C LN=#NUM COL=#NUM>`  | Move the cursor the row NUM and col NUM               |
| `<?C ONE-UP>`            | Move cursor one line up, scrolling if needed          |
| `<?C GET-POS>`           | Report cursor position by transmitting &ESC;[n;mR     |

### Page scroll instructions

| Code example        | Description                   |
| ------------------- | ----------------------------- |
| `<?SCRL UP=#NUM>`   | Scroll page up by NUM lines   |
| `<?SCRL DOWN=#NUM>` |	Scroll page down by NUM lines |

### Delete instructions

| Code example          | Description                              |
| --------------------- | ---------------------------------------- |
| `<?DEL CHAR>`         | Insert `&DEL;` character                 |
| `<?DEL SCREEN-END>`   | Erase from cursor until end of screen    |
| `<?DEL SCREEN-START>` | Erase from cursor to beginning of screen |
| `<?DEL SCREEN>`       | Erase entire screen                      |
| `<?DEL SCREEN-SAVED>` | Erase entire screen and saved lines      |
| `<?DEL LINE-END>`     | Erase from cursor to end of line         |
| `<?DEL LINE-START>`   | Erase from start of line to cursor       |
| `<?DEL LINE>`         | Erase the entire line                    |

### Reset instructions

| Code example     | Description                                                               |
| ---------------- | ------------------------------------------------------------------------- |
| `<?RESET STYLE>` | Reset style options (`<B, D, I, U, BLINK, INVERT, HIDE, S>`)              |
| `<?RESET FG>`    | Reset the foreground color                                                |
| `<?RESET BG>`    | Reset the background color                                                |
| `<?RESET COLOR>` | Reset both FG and BG (same as `<?RESET FG BG>`)                           |
| `<?RESET ALL>`   | Reset everything that can be reset to its defaults with options ("ESC[m") |
| `<?RESET TERM>`  | Fully reset the terminal, potentially deleting all content ("ESC c")      |

## Useful references

* Nice ref: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
* More: https://en.wikipedia.org/wiki/ANSI_escape_code