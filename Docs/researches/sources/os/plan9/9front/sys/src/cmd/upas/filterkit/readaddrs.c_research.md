# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/readaddrs.c

This file parses address files into `Addr` linked lists.

Key behavior:
- `emalloc` and `estrdup` fatal on allocation failure.
- `tokenize822` splits on space/tab/newline but honors double-quoted strings.
- `readaddrs` appends parsed tokens from a file to the end of an existing `Addr` list.
- Reads at most 8191 bytes from the address file.

Integration and risks:
- The tokenizer mutates the buffer in place.
- Quoted-string handling is minimal and not a full RFC 822 parser.
