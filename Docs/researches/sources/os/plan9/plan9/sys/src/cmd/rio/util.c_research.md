# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/util.c

Read status: complete, 149 lines.

This utility file provides UTF conversion, fatal error handling, allocation helpers, rune classification/search, min/max, and rune-to-byte conversion.

`cvttorunes` converts byte buffers into runes while eliding NULs and reporting them. `runetobyte` allocates a UTF-8 byte string from a rune slice. `isalnum` is intentionally broad for non-ASCII characters to support word selection.

Filesystem relevance: supports text conversion for `/dev/cons`, `/dev/text`, `/dev/snarf`, and other byte-oriented window files.
