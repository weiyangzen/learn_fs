# File Research: sources/os/bsd/netbsd-src/sys/sys/ansi.h

Read completely: 76 lines.

Defines NetBSD's internal ANSI/base typedef substrate after including machine-specific `ansi.h`.

Key elements:
- Provides internal typedefs for core address, gid, IPv4 address/port, mode/access mode, offset, pid, socket family/length, uid, filesystem block/file counts, wide-character classification/translation handles, multibyte conversion state, and va_list.
- `__mbstate_t` is an opaque 128-byte union aligned by an `int64_t`.
- Exposes `_BSD_WCTRANS_T_`, `_BSD_WCTYPE_T_`, and `_BSD_MBSTATE_T_` macro aliases for public type plumbing.
- Uses `__builtin_va_list` except under lint, where `char *` is used.

Risks and notes:
- These typedefs underpin many public headers; changing widths affects ABI.
- The header deliberately uses internal names to support standards-visible typedef construction elsewhere.
