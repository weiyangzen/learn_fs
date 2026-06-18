# File Research: sources/os/bsd/netbsd-src/lib/libcompat/regexp/regmagic.h

Read completely: 7 lines.

Defines the magic byte `MAGIC` (`0234`) used as the first byte of compiled legacy regexp programs. `regexp.c` writes this before the first node, and `regexp.c`/`regsub.c` validate it before execution or substitution.

The file is intentionally tiny but important for ABI/data-format consistency between the compiler, executor, and substitution helper. A mismatched value would make valid compiled regexps appear corrupt.
