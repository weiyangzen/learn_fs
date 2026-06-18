# File Research: sources/os/plan9/9front/sys/src/cmd/sam/address.c

`address.c` evaluates sam address syntax into concrete file ranges. It supports character addresses, line addresses, dot, end of file, mark, forward/backward regex search, file-name regex selection, whole file, compound comma/semicolon ranges, and relative `+`/`-` movement.

`address` walks an `Addr` parse tree and updates both the current `Address` and the current file where required. Semicolon ranges set dot after evaluating the left side, matching sam's address semantics.

`nextmatch` compiles the regex and runs forward `execute` or backward `bexecute`, avoiding zero-length self-matches at the starting position by advancing/wrapping and retrying.

`matchfile` and `filematch` implement quoted file-address matching against the menu-style representation of open files. They build a temporary menu line containing modified state, rasp state, current-file marker, and filename, then run the regex against that synthetic file.

`charaddr` applies absolute or relative rune-position addressing and checks bounds. `lineaddr` maps line counts to ranges by scanning file runes and handles forward/backward movement, line zero, EOF, and range validation.
