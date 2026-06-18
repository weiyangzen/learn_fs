# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/gettemp.c

Provides the shared `GETTEMP()` implementation behind `mkstemp`, `mkstemps`, `mkostemp`, `mkdtemp`, `mktemp`, `tmpnam`, and `tempnam`. It validates arguments, suffix length, allowed open flags, and path length; replaces trailing `X` characters with random base-62 characters; checks parent directory validity for create operations; then tries to create/open/test the generated path.

Collision handling cycles deterministically through the generated character space using a saved initial carry buffer. For creation, it uses `open(..., O_CREAT|O_EXCL|O_RDWR|oflags, 0600)` or `mkdir(..., 0700)`; for name-only generation it checks `lstat()` and succeeds only if the path is absent.
