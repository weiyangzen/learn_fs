# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dirent_.h

This is a portability shim for Unix directory-entry headers in Ghostscript.

Key responsibilities:
- Includes `std.h` before any system header that may include `sys/types.h`.
- Includes `gconfig_.h`, whose configure/build-time macros describe which directory-entry header exists on the target.
- If `HAVE_DIRENT_H` is set, includes `<dirent.h>` and typedefs `struct dirent` as `dir_entry`.
- Otherwise conditionally includes older alternatives `<sys/dir.h>`, `<sys/ndir.h>`, or `<ndir.h>`, then typedefs `struct direct` as `dir_entry`.

Important dependencies:
- The header is declared in `lib.mak` as `dirent__h=$(GLSRC)dirent_.h $(std_h) $(gconfig__h)`.
- It is used by Unix filesystem portability code such as `gp_unifs.c`.

Notable implementation details:
- The public abstraction is intentionally tiny: one normalized `dir_entry` typedef.
- Header selection is entirely macro-driven; no runtime behavior is present.
- It supports older Unix systems that predate or do not expose POSIX `dirent.h`.

Filesystem relevance:
- This is adjacent to filesystem portability because it normalizes directory enumeration structures for Ghostscript's platform layer.
- It does not implement directory traversal, path lookup, VFS behavior, or storage logic itself.

Research classification: small Ghostscript portability header for directory-entry type normalization.
