# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jconfig0.h

Generated-style Ghostscript JPEG configuration header used when `SHARE_JPEG=0`. It is not only IJG `jconfig.h`; it is a concatenation of Ghostscript portability headers (`stdpn.h`, `stdpre.h`) and `gsjconf.h`, arranged this way because `jpeg.mak` builds IJG sources in a directory layout where the normal Ghostscript include order is not available.

The first section defines deprecated `P0` through `P16` prototype-list macros. They now expand directly to ANSI prototype lists and exist only for old Ghostscript source compatibility.

The `stdpre` portion normalizes compiler and platform feature macros, including `__MSDOS__`, `__OSF__`, `SYSV`, `__SVR3`, and `__PROTOTYPES__`. It provides fallback `__FILE__`/`__LINE__`, manages `const`, `volatile`, and `inline`, defines `extern_inline` support for GCC, and supplies generic portability macros such as `DISCARD`, `size_of`, `countof`, `offset_of`, `ALIGNMENT_MOD`, pointer-order comparisons, `min`, `max`, `ROUND_UP`, and `ROUND_DOWN`.

It also establishes Ghostscript common scalar types and conventions: `byte`, `uchar`, `ushort`, `uint`, `ulong`, `bool`, `true`, `false`, `floatp`, `client_name_t`, `public`, `private`, `BEGIN`, `END`, `DO_NOTHING`, and portable `exit_OK`/`exit_FAILED`. The header temporarily renames `bool` and unsigned typedef names before including `<sys/types.h>` to avoid conflicts.

The final `gsjconf.h` portion is the actual IJG configuration. It includes `arch.h`, maps Ghostscript prototype detection to IJG `HAVE_PROTOTYPES`, enables `HAVE_UNSIGNED_CHAR` and `HAVE_UNSIGNED_SHORT`, conditionally enables `HAVE_STDDEF_H` and `HAVE_STDLIB_H`, and undefines `CHAR_IS_UNSIGNED`, `NEED_BSD_STRINGS`, `NEED_SYS_TYPES_H`, `NEED_FAR_POINTERS`, `NEED_SHORT_EXTERNAL_NAMES`, and `INCOMPLETE_TYPES_BROKEN`.

JPEG-internal settings depend on Ghostscript architecture macros: `MAX_ALLOC_CHUNK` is reduced on systems with 16-bit-or-smaller `int`, and `RIGHT_SHIFT_IS_UNSIGNED` is set only when `ARCH_ARITH_RSHIFT == 0`.

Notable dependencies:
- Includes `<sys/types.h>` inside the portability section.
- Includes `arch.h` for Ghostscript architecture sizing and arithmetic-shift configuration.
- Expected to be generated/copied as `jconfig.h` by `jpeg.mak`.

Filesystem relevance: indirect. This is part of the Plan 9/9front Ghostscript userland build, specifically image codec configuration for PostScript/PDF processing, not kernel filesystem logic.
