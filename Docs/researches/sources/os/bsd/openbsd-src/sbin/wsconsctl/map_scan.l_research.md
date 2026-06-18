# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/map_scan.l

Lex scanner for keyboard map input.

Key behavior:
- Skips whitespace.
- Returns tokens for `=`, `keycode`, and `keysym`.
- Converts key symbol names through `name2ksym()`.
- Classifies command keysyms separately from ordinary keysyms.
- Parses decimal numbers with `strtonum()`.
- Rejects illegal characters with printable or octal diagnostics.
- `map_scan_setinput()` feeds a string into the scanner with `yy_scan_string()`.

Filesystem/OS relevance:
- Provides robust input validation before keymap data reaches wskbd ioctls.
