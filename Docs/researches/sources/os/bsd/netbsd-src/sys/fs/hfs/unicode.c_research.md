# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/unicode.c

## Purpose
Provides local UTF-8 to UTF-16 and UTF-16 to UTF-8 conversion helpers for HFS path and directory name handling.

## Main Entry Points
- `utf8_to_utf16()` decodes UTF-8 into UTF-16 code units, optionally falling back to Latin-1 for invalid high bytes, rejects some malformed encodings, emits surrogate pairs for four-byte UTF-8, and returns output code-unit count.
- `utf16_to_utf8()` encodes UTF-16 code units into UTF-8 bytes, attempting to handle surrogate pairs, and returns byte count.

## Dependencies
Uses `sys/null.h` and declarations from `unicode.h`.

## Risks and Notes
The implementation is compact but fragile. Several bounds checks test `spos >= src_len` instead of checking whether `spos + needed` is in range, so truncated multibyte input can read past the provided buffer. `utf16_to_utf8()` uses `uint8_t` loop/output positions, which can overflow for lengths above 255. The surrogate-pair path appears to test the first surrogate twice rather than validating the second code unit and can index past the pair after incrementing. Error counts are reported but most HFS callers ignore them.
