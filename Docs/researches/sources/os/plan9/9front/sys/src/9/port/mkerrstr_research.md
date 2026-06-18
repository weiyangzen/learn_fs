# File Research: sources/os/plan9/9front/sys/src/9/port/mkerrstr

Tiny `rc`/`sed` generator for kernel error-string definitions.

Key behavior:
- Reads `../port/error.h`.
- Transforms `extern` declarations with comments into C string definitions of the form `name = "comment";`.

Role:
- Produces `errstr.h`, included by `proc.c`, so portable kernel error symbols become concrete strings.
