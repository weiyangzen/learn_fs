# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_file.c

File-backed address-list loader.

Key behavior:
- Opens `filename + 7`, matching `file://` URI inputs.
- Reads one address/list item per line.
- Handles comments, leading/trailing whitespace, CRLF, and leading `!` negation.
- Builds an `alist_t` linked list with `alist_new()`.

Research notes:
- Lines without newline are treated as too long and abort parsing.
- Because it always skips seven bytes, callers passing plain paths must already account for that offset; `load_url.c` does not appear to.
