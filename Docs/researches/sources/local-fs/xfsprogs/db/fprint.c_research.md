# File Research: sources/local-fs/xfsprogs/db/fprint.c

Purpose: implements primitive field print functions used by `ftattrtab`.

Key behavior:
- `fp_charns` prints character arrays as quoted strings with C-style escaping for quotes, backslashes, printable characters, control characters, and octal escapes.
- `fp_num` prints numeric fields with signed/unsigned extraction, null formatting, zero/null skipping, array index prefixes, and 32-bit versus 64-bit format handling.
- `fp_sarray` delegates structured array printing to `print_sarray`.
- `fp_time` prints inode timestamp seconds as human-readable time when representable by `time_t`, otherwise raw seconds.
- `fp_nsec` prints inode timestamp nanoseconds.
- `fp_qtimer` prints quota timers, preserving raw values for root/default or non-expired timers and formatting expiration times otherwise.
- `fp_uuid` prints UUIDs using platform UUID formatting.
- `fp_crc` prints CRC values plus verification state: unchecked, bad, correct, or unknown.

Interactions:
- Print functions are referenced by `field.c` field attributes.
- Uses bit extraction from `bit.c`, print helpers, current IO CRC status, signal interruption checks, and libxfs timestamp conversions.

Risks/notes:
- Formatting honors `seenint()` so long output can be interrupted.
- Human-readable timestamp output is intentionally guarded against `time_t` range loss.
