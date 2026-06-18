# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_memstream.c

Memory-backed stream helpers for parsing mapped files and regions.

Key behavior:
- `_citrus_memory_stream_getln` returns the next line region and advances position.
- `_citrus_memory_stream_matchline` scans for a key at the start of parsed non-comment lines and returns the data portion.
- `_citrus_memory_stream_chr` returns the region up to a delimiter and advances past it.
- `_citrus_memory_stream_skip_ws` consumes BCS whitespace.

Parsing rules:
- Comment delimiter is `#`.
- Matching trims trailing whitespace/newlines, skips leading whitespace, and compares first token case-sensitively or insensitively.
