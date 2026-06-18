# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsutil.c

Implements miscellaneous Ghostscript library utilities for IDs, bit transposition, byte parsing, string matching, UID handling, and rectangle subtraction.

Key behavior:
- `gs_next_ids` reserves a contiguous block from the library context's monotonically increasing ID counter.
- `memflip8x8` transposes an 8-by-8 bit block, including fast paths for all-identical bytes and all-zero/all-one inputs.
- `get_u32_msb` parses a big-endian 32-bit unsigned value.
- `bytes_compare` compares arbitrary byte strings lexicographically with unsigned byte semantics.
- `string_match` implements wildcard matching with configurable any-substring, any-char, quote, case-insensitive, and slash-equivalence behavior.
- `uid_equal` compares UniqueIDs or XUID vectors; `uid_copy` deep-copies XUID arrays into Ghostscript memory.
- `int_rect_difference` mutates an outer rectangle to its intersection with an inner rectangle and emits up to four difference rectangles.

Dependencies:
- Uses Ghostscript memory allocation/error conventions and UID/type definitions from `gsmemory.h`, `gsuid.h`, and `gstypes.h`.
- Rectangle utility prototypes are tied to `gsrect.h`.

Research notes:
- `string_match` uses a single backtracking point for `*` and includes special Windows path slash equivalence when requested.
- `int_rect_difference` assumes rectangle interval semantics from the common type definitions.
