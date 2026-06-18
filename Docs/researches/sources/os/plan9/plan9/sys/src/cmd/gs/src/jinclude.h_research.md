# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jinclude.h

## Identity

- Lines/bytes: 91 lines, 3,250 bytes.
- SHA-256: `a6433e5ea0030f4bffd41bcc2f064008afd79de4270cf28494bd43d2fbc5da06`.
- Role: IJG internal include-normalization header.

## Contents

The file:

- Includes `jconfig.h` and sets `JCONFIG_INCLUDED`.
- Pulls in standard headers based on `HAVE_STDDEF_H`, `HAVE_STDLIB_H`, and `NEED_SYS_TYPES_H`.
- Always includes `stdio.h` because public IJG API declarations reference `FILE`.
- Provides `MEMZERO` and `MEMCOPY` using either BSD `bzero`/`bcopy` or ANSI/SysV `memset`/`memcpy`.
- Defines `SIZEOF(object)` as a `size_t` casted `sizeof`.
- Defines `JFREAD` and `JFWRITE` wrappers around `fread`/`fwrite`.

## Dependencies

- Requires `jconfig.h`.
- May include `stddef.h`, `stdlib.h`, `sys/types.h`, `stdio.h`, `strings.h`, or `string.h` depending on configuration macros.

## Behavior And Integration

- Used by IJG implementation files, not intended for JPEG library applications.
- Centralizes portability decisions around memory, file I/O, `NULL`, and `size_t`.

## Research Notes

- Ghostscript’s `jpeg.mak` copies this header into the generated directory so IJG sources pick up Ghostscript’s generated `jconfig.h`.
- No filesystem-specific behavior is present.
