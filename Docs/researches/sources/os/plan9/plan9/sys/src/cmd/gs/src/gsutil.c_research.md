# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsutil.c

Purpose: Provides miscellaneous Ghostscript utility implementations for IDs, bit transposition, endian reads, string matching, UID operations, and integer rectangle difference.

Key functions:
- `gs_next_ids()` reserves a block of library-wide unique IDs from `mem->gs_lib_ctx`.
- `memflip8x8()` transposes an 8x8 bit block when assembly replacement is not enabled.
- `get_u32_msb()` reads an unsigned 32-bit big-endian integer.
- `bytes_compare()` lexicographically compares unsigned byte strings.
- `string_match()` performs wildcard matching with configurable `*`, `?`, quote, case-insensitive, and slash-equivalence behavior.
- `uid_equal()` and `uid_copy()` implement UID comparison/copying for `gsuid.h`.
- `int_rect_difference()` subtracts an inner rectangle from an outer rectangle, returning up to four difference rectangles.

Behavior:
- `memflip8x8()` includes a fast path for all-zero/all-one or identical rows and then uses register-level transpose steps.
- `string_match()` uses backtracking only around the most recent wildcard.
- `int_rect_difference()` mutates `outer` to the intersection-like remaining central rectangle while filling `diffs`.

Dependencies:
- Uses Ghostscript memory allocation APIs, debug fill conventions, `gstypes.h`, `gsrect.h`, `gsuid.h`, and `gsutil.h`.

Notable risks:
- `gs_next_ids()` is a simple increment with no local locking visible here.
- `string_match()` treats a trailing quote in the pattern as a successful match path, matching historical behavior.
