# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/misc.c

Miscellaneous Antiword support routines shared across parsing, conversion, layout, locale setup, and diagnostics.

Key responsibilities:
- Finds user and Antiword configuration directories, with platform branches for VMS, Plan 9, DOS, NetWare, and RISC OS.
- Provides file-size and positioned-read helpers, including `bReadBuffer()` for following Word big/small block depot chains.
- Implements output-list splitting, Roman/alpha numbering, color mapping, basename extraction, line-leading calculation, zero-buffer checks, UCS-to-UTF-8, and bullet rendering.
- Converts counted Word Unicode strings to configured single-byte output and measures null-terminated UTF-16 byte length.
- Normalizes locale codeset names and chooses default character mapping files for non-RISC OS builds.
- Converts Word DTTM packed date/time values to `time_t`.

Dependencies:
- Uses `antiword.h` core types and helpers such as `xmalloc`, `xfree`, `werr`, `ulDepotOffset`, `lComputeStringWidth`, `ulTranslateCharacters`, and endian accessors.
- Uses C/POSIX file APIs, locale environment variables, `stat`, and `mktime`.

Notable risks:
- `bReadBuffer()` detects out-of-range depot indexes but does not detect cyclic block chains.
- File offsets are constrained through `long`/`ULONG`; very large files are rejected or truncated by design.
- Locale parsing is handcrafted and assumes classic `language[_territory][.codeset][@modifier]` formatting.
