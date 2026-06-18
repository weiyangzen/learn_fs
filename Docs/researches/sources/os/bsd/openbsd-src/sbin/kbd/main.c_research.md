# File Research: sources/os/bsd/openbsd-src/sbin/kbd/main.c

`main.c` is the entry point for `kbd`. It parses `-l` to list keyboard tables and `-q` to suppress successful set messages.

The argument contract is either `kbd -l` or `kbd [-q] name`. It dispatches to `kbd_list()` or `kbd_set()` and exits.

The file contains no device logic; it is command-line validation and dispatch.
