# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep.h

## Purpose
UTF-8/Unicode conversion, validation, comparison, and normalization option definitions.

## Main Interfaces
- Defines Unicode conversion endian/BOM/null handling flags for UTF-8, UTF-16, and UTF-32 conversion.
- Declares `uconv_u16tou8`, `uconv_u32tou8`, `uconv_u8tou16`, and `uconv_u8tou32`.
- Defines string comparison and normalization flags for case-sensitive/case-insensitive comparison, canonical/compatibility decomposition, canonical composition, NFD/NFC/NFKD/NFKC, uppercase/lowercase mapping, ignore-null, ignore-invalid, and no-wait behavior.
- Defines Unicode version selectors `U8_UNICODE_320`, `U8_UNICODE_500`, and `U8_UNICODE_LATEST`.
- Defines validation flags and illegal/out-of-range character sentinel values.
- Declares `u8_validate`, `u8_strcmp`, and kernel-only text preparation routines.

## Dependencies And Relationships
Includes `sys/isa_defs.h`, `sys/types.h`, and `sys/errno.h`. Used by filesystem/name handling and other consumers needing Unicode-normalized string behavior.

## Research Notes
The API combines conversion and normalization controls. Callers must choose flags carefully because comparison can imply normalization and case conversion.
