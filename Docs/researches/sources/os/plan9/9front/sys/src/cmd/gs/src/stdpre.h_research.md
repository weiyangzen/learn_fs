# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stdpre.h

Standard definitions that do not require `arch.h`.

Key points:
- Normalizes compiler/platform feature macros such as `__MSDOS__`, `__OSF__`, `SYSV`, `__SVR3`, and `__PROTOTYPES__`.
- Provides fallbacks for `__FILE__`, `__LINE__`, `const`, `volatile`, and `inline`.
- Defines `extern_inline` policy, `DISCARD`, `size_of`, `far_data`, `countof`, `offset_of`, and `ALIGNMENT_MOD`.
- Defines Ghostscript short unsigned aliases: `byte`, `uchar`, `ushort`, `uint`, and `ulong`.
- Includes `<sys/types.h>` behind temporary macro renames to avoid type-name clashes.
- Defines portable `bool`, `true`, `false`, pointer comparison macros, `min`, `max`, `ROUND_UP`, `ROUND_DOWN`, `floatp`, `BEGIN`/`END`, `DO_NOTHING`, and `client_name_t`.
- Defines `public`/`private` conventions and includes `stdpn.h`.
- Defines portable `exit_OK` and `exit_FAILED`, with VMS special handling.

Dependencies and interactions:
- Included before most Ghostscript headers.
- Its requirement to include `std.h` before headers using `sys/types.h` drives wrappers like `stat_.h`, `stdio_.h`, `string_.h`, and `time_.h`.

Research relevance:
- Foundational portability layer for old C compilers, system headers, pointer ordering, basic types, and Ghostscript coding conventions.
