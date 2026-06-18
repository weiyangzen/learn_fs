# File Research: sources/os/plan9/9front/sys/src/cmd/vac/error.c

`error.c` defines shared vac error strings such as missing directory entry, no file, bad path, corrupted metadata, not directory/file, I/O error, bad offset, too big, read-only, removed, illegal block address, directory not empty, existing file, and root removal.

The strings are exported as mutable global char arrays matching declarations in `error.h`, allowing code to compare or pass stable Plan 9-style error text.
