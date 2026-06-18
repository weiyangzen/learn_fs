# File Research: sources/os/bsd/netbsd-src/lib/libc/nls/catopen.c

Implementation of `catopen()` and `catopen_l()`. Absolute or relative catalog names are loaded directly; bare names are expanded through `NLSPATH` unless set-id, otherwise the built-in default path is used.

Locale selection uses `LC_MESSAGES` from the supplied locale for `NL_CAT_LOCALE`, otherwise `LANG`, with slash-containing or missing locale names falling back to `C`. It resolves aliases through `/usr/share/nls/nls.alias`, expands `%L` and `%N` path substitutions, and tries each path element.

`load_msgcat()` opens the catalog close-on-exec, mmaps it read-only, checks `_NLS_MAGIC`, and returns an allocated descriptor storing the map and size.
