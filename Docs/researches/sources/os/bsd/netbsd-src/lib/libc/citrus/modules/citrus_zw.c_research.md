# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_zw.c

## Scope

Implements the Citrus ctype/stdenc module for the ZW encoding, a stateful ASCII/GB2312-style encoding using `zW` shift sequences.

## APIs And Behavior

- Maintains `_ZWState` with charset state: `NONE`, `AMBIGIOUS`, `ASCII`, or `GB2312`.
- `_citrus_ZW_mbrtowc_priv()` decodes ASCII, recognizes `zW` entry into GB2312 mode, handles newline/NUL reset behavior, and decodes two-byte GB2312 indexes.
- `_citrus_ZW_wcrtomb_priv()` emits `zW` when entering GB2312 mode, encodes ASCII escapes inside GB2312 mode, and emits GB2312 pairs for non-ASCII values.
- `_citrus_ZW_put_state_reset()` emits newline to leave GB2312 mode when needed.
- Stdenc uses csid `0` for ASCII-range values and `1` for others.

## Dependencies

Uses Citrus ctype/stdenc templates and standard wide-character/errno APIs.

## Risks And Invariants

- State transitions around `z`, `zW`, newline, and NUL are subtle and affect stream synchronization.
- All encoded bytes are constrained to 7-bit values; bytes above `0x7f` are rejected.
- Reset output is required for stateful GB2312 mode.
