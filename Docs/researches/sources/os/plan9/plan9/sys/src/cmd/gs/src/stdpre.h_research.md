# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdpre.h

Purpose: compiler and platform portability foundation used before architecture-specific setup.

Key contents:
- Normalizes platform symbols such as `__MSDOS__`, `SYSV`, `__SVR3`, and `__OSF__`.
- Detects prototype support and conditionally disables `const`, `volatile`, and `inline`.
- Defines inline support conventions through `extern_inline` and `HAVE_EXTERN_INLINE`.
- Provides `DISCARD`, `size_of`, `countof`, `offset_of`, `ALIGNMENT_MOD`, `ROUND_UP`, and `ROUND_DOWN`.
- Defines Ghostscript short unsigned aliases (`byte`, `uchar`, `ushort`, `uint`, `ulong`) and carefully avoids `sys/types.h` conflicts.
- Defines non-C++ `bool`, `true`, `false`, pointer comparison macros, `floatp`, `BEGIN`/`END`, `DO_NOTHING`, `client_name_t`, `public`, `private`, and process exit constants.
- Includes `stdpn.h`.

Dependencies: `<sys/types.h>`, `stdpn.h`.

Integration notes: this is the base for most files in the batch via `std.h`.

Risks: macro definitions such as `private`, `public`, and boolean aliases can conflict with external headers if include ordering is wrong.
