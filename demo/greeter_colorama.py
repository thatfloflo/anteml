import re
import sys
from colorama import init as init_colorama, Fore, Back, Style
from typing import Pattern

version: str = "1.0.0"
name_pattern: Pattern[str] = re.compile(
    r"\A\w[\w ]+\w\Z",
    re.UNICODE
)
init_colorama()

print(
    f"{Fore.BLACK}{Back.WHITE}Welcome to the {Style.BRIGHT}{Fore.RED}People "
    f"Greeter{Fore.BLACK}{Style.NORMAL} {Style.DIM}(version {version})"
    f"{Style.NORMAL}{Back.RESET}{Fore.RESET}!\n"
)
print(
    f"Please type your name: {Style.DIM}{Fore.CYAN}(confirm with Enter)"
    f"{Fore.RESET}{Style.NORMAL}"
)

while True:
    name = input("\x1b[3m").strip()
    print("\x1b[23m", end="")
    if name_pattern.fullmatch(name):
        break
    print(
        f"{Style.DIM}{Fore.RED}Oops, the string {name!r} doesn't look like a "
        f"valid name...{Fore.RESET}\n"
        f"{Style.DIM}{Fore.CYAN}A name should be at least 2 characters and "
        f"consist only of unicode word characters and spaces.{Fore.RESET}\n"
        f"{Style.NORMAL}Please try again:"
    )

print(
    f"\n{Style.BRIGHT}Welcome, {Fore.BLACK}{Back.WHITE}{name}"
    f"{Fore.RESET}{Back.RESET}!\n"
    f"{Fore.GREEN}Be greeted!{Style.RESET_ALL}"
)

sys.exit(0)