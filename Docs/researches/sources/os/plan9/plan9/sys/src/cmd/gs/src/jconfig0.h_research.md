# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jconfig0.h

## Identity

- Lines/bytes: 571 lines, 19,233 bytes.
- SHA-256: `22e46945a19903137379d8460420bb3de098d9e846bc1388dddd513bd177979a`.
- Role: generated-style Ghostscript `jconfig.h` source for IJG JPEG builds when Ghostscript compiles its private JPEG copy.

## Contents

This file is a concatenation of three Ghostscript headers:

- `stdpn.h`: deprecated `P0` through `P16` prototype-list macros retained for old Ghostscript source compatibility.
- `stdpre.h`: Ghostscript portability prelude defining compiler/platform feature macros, `inline`/`extern_inline`, `DISCARD`, `size_of`, `countof`, pointer comparison macros, unsigned short-name typedefs, `bool`/`true`/`false`, `BEGIN`/`END`, `public`/`private`, exit status macros, and inclusion of `stdpn.h`.
- `gsjconf.h`: Ghostscript’s IJG `jconfig.h` configuration, including `arch.h`, prototype support, unsigned type availability, standard-header availability under `__STDC__`, allocation chunk handling for small `int`, and right-shift behavior for JPEG internals.

## Dependencies

- Includes `sys/types.h` through the `stdpre.h` section.
- Includes `stdpn.h` through the `stdpre.h` section, although the file already contains a copy of `stdpn.h` at the front.
- Includes `arch.h` in the `gsjconf.h` section.
- Build rule in `jpeg.mak` constructs this from `stdpn.h`, `stdpre.h`, and `gsjconf.h`.

## Behavior And Integration

- Controls how IJG code sees compiler capabilities and platform details.
- Defines `HAVE_PROTOTYPES`, `HAVE_UNSIGNED_CHAR`, `HAVE_UNSIGNED_SHORT`, `HAVE_STDDEF_H`, and `HAVE_STDLIB_H`.
- Leaves BSD strings, sys/types need, far pointers, short external names, and incomplete-type workaround disabled.
- Defines `RIGHT_SHIFT_IS_UNSIGNED` only when `JPEG_INTERNALS` is set and `ARCH_ARITH_RSHIFT == 0`.
- On 16-bit or smaller `int`, lowers `MAX_ALLOC_CHUNK` to `0xfff0`.

## Research Notes

- This is infrastructure for Ghostscript’s bundled JPEG library, not Plan 9 kernel/VFS code.
- It is important because downstream IJG headers and sources rely on the generated `jconfig.h` for ABI-visible type and feature choices.
- The file’s concatenated structure exists because Ghostscript’s JPEG build copies/generated headers into an intermediate directory to force IJG sources to include Ghostscript’s configuration.
