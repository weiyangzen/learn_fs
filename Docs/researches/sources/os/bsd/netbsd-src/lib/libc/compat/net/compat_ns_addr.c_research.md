# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/net/compat_ns_addr.c

Read completely: 244 lines.

This implements legacy Xerox NS address parsing in `ns_addr`. It accepts multiple historical syntaxes using `.`, `:`, or `#` separators, parses network/host/port fields in decimal, octal, hexadecimal, dash-separated decimal chunks, dotted/colon hex bytes, and comma-separated shorts, then converts arbitrary-base chunks into byte arrays.

Important interactions: fills a static `struct ns_addr`, so callers receive a pointer-stable but non-thread-local global result pattern. It depends on compatibility `ns.h` and endian helpers for socket/port layout.

Security/reliability notes: input is copied into a fixed 50-byte buffer with `strlcpy`, so long strings are truncated before parsing. Numeric parsing with `sscanf` is permissive and legacy-oriented; malformed suffixes often just terminate parsing rather than fail explicitly.
