from time import sleep
from anteml.parser import AntemlParser

def print_(x: str):
    print(x, end="")

parser = AntemlParser(receiver=print_, strip_unknown=False)

parser.feed("<B>=== 256-COLOR DECIMAL BACKGROUND ===</B><BR>")
for i in range(0x00, 0xFF+1):
    parser.feed(f"<bg D{i:03}>&nbsp;D{i:03}&nbsp;</bg>")
    if i % 16 == 15:
        parser.feed("<BR>") 
parser.feed("<BR>")

parser.feed("<B>=== FULL-COLOR HEXADECIMAL-TRIPLET BACKGROUND ===</B><BR>")
for r in range(0x0, 0xF):
    for g in range(0x0, 0xF):
        for b in range(0x0, 0xF):
            parser.feed(f"<bg X{r:X}{g:X}{b:X}>&nbsp;</bg>")
    parser.feed("<BR>")
parser.feed("<BR>")

parser.feed("<B>=== FULL-COLOR HEXADECIMAL BACKGROUND ===</B><BR>")
response = input("Do you want to print over 16-million colors? [y/N] ")
if response.lower() in ("y", "yes"):
    try:
        print("Okay, here we go!")
        sleep(1)
        for r in range(0x00, 0xFF):
            for g in range(0x00, 0xFF):
                for b in range(0x00, 0xFF):
                    parser.feed(f"<bg X{r:02X}{g:02X}{b:02X}>&nbsp;</bg>")
        parser.feed("<BR>")
        parser.feed(f"Congratulations, you survived the <I>Torrent of {0xFFFFFF} Colors</I>!<BR>")
    except KeyboardInterrupt:
        parser.feed("<BR><?RESET ALL>")
        print("Okat, got it, that's enough :)")
else:
    print("Fair enough, we'll let that one slide then!")