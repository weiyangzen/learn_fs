# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jinclude.h

IJG internal support header that centralizes system includes and standard-library compatibility macros for the JPEG implementation. It is intended for JPEG library source files, not for applications, which should include `jpeglib.h`.

The header starts by including `jconfig.h` and defining `JCONFIG_INCLUDED` so `jpeglib.h` does not include configuration a second time. Based on `jconfig.h`, it optionally includes `<stddef.h>`, `<stdlib.h>`, and `<sys/types.h>`, then unconditionally includes `<stdio.h>` because the public API exposes `FILE *` in the stdio source/destination managers.

It selects memory helper macros from either BSD or ANSI/System V string APIs:
- With `NEED_BSD_STRINGS`, includes `<strings.h>` and maps `MEMZERO` to `bzero`, `MEMCOPY` to `bcopy`.
- Otherwise, includes `<string.h>` and maps `MEMZERO` to `memset`, `MEMCOPY` to `memcpy`.

It defines `SIZEOF(object)` as a `size_t`-cast wrapper around `sizeof`, and wraps stdio byte I/O as `JFREAD(file, buf, sizeofbuf)` and `JFWRITE(file, buf, sizeofbuf)`, preserving IJG's argument order while casting counts and pointers consistently.

Notable dependencies:
- `jconfig.h`, generated from `jconfig0.h` or a shared-JPEG stub by `jpeg.mak`.
- Standard C headers selected by the generated configuration.

Filesystem relevance: none directly. It affects JPEG file stream I/O through `FILE *`, but not Plan 9 filesystem internals.
