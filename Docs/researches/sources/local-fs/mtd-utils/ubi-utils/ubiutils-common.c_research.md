# File Research: sources/local-fs/mtd-utils/ubi-utils/ubiutils-common.c

## Purpose
Provides shared helper routines used by UBI utilities for byte-size parsing, byte-size formatting, text wrapping, and pseudo-random seeding.

## Main Entry Points
- `ubiutils_get_bytes()` parses numeric byte strings with optional `KiB`, `MiB`, or `GiB` suffixes.
- `ubiutils_print_bytes()` prints exact bytes plus an approximate KiB/MiB/GiB representation when useful.
- `ubiutils_print_text()` wraps long text to a requested column width.
- `ubiutils_srand()` seeds libc `rand()` from current time and process ID.

## Internal Mechanics
`get_multiplier()` accepts only binary suffixes and skips spaces or tabs before the suffix. `ubiutils_get_bytes()` uses `strtoull()` with base auto-detection, then multiplies by the suffix multiplier if present. `ubiutils_print_text()` builds each folded line in a fixed 1024-byte buffer and breaks either at whitespace or hard width. `ubiutils_srand()` combines seconds, microseconds, and PID, reduces the seed modulo `RAND_MAX`, and calls `srand()`.

## Dependencies
Uses libc time, string, character classification, process, and standard I/O APIs. Includes local `common.h` for shared utility context and is declared to callers through `ubiutils-common.h`.

## Risks and Notes
`ubiutils_get_bytes()` stores `strtoull()` output in a signed `long long`; out-of-range conversions and values above `LLONG_MAX` are not explicitly checked via `errno`, so very large inputs can wrap or become implementation-dependent before the `bytes < 0` check. Suffix multiplication can overflow `long long`. `ubiutils_print_text()` assumes `width > 0`; zero or negative widths would produce invalid indexing behavior.
