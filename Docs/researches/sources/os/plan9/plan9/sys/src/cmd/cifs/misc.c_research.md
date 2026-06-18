# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/misc.c

Tiny ASCII case-conversion helpers. `strupr` uppercases in place; `strlwr` lowercases in place. Both skip negative `char` values before calling ctype macros.

Used for share/path normalization in the CIFS client.
