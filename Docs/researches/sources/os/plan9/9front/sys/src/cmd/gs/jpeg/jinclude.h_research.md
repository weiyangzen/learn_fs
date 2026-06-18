# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jinclude.h

Purpose: internal IJG portability include.

Key contents:
- Includes `jconfig.h`.
- Defines `JCONFIG_INCLUDED` so `jpeglib.h` does not include configuration again.
- Centralizes system header selection for JPEG library modules.
- Pulls in headers for `NULL`, `size_t`, `FILE`, allocation, and string/memory functions based on configuration symbols.
- Defines `MEMZERO` and `MEMCOPY` through BSD `bzero`/`bcopy` or ANSI `memset`/`memcpy`.
- Defines `SIZEOF(object)` as a `size_t`-cast `sizeof`.
- Defines `JFREAD` and `JFWRITE` wrappers around `fread`/`fwrite`.

Notes:
- Not intended for application code; applications are expected to include `jpeglib.h`.
