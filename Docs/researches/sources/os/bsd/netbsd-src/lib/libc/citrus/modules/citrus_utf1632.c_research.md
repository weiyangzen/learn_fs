# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf1632.c

## Scope

Implements the Citrus stdenc module for UTF-16 and UTF-32, including BOM detection/emission, preferred endian selection, forced-endian mode, and surrogate-pair handling.

## APIs And Behavior

- `_citrus_UTF1632_mbrtowc_priv()` reads 2 or 4 bytes depending on UTF-16/UTF-32 mode, detects BOM unless forced, and decodes UTF-16 surrogate pairs.
- `_citrus_UTF1632_wcrtomb_priv()` emits an initial BOM unless forced-endian mode is active, then writes UTF-16 code units or UTF-32 words in current endian.
- `parse_variable()` recognizes `big`, `little`, `force`, and `utf32`.
- Module init sets maximum byte length to 6 for UTF-16 or 8 for UTF-32, accounting for initial BOM plus character bytes.
- Stdenc maps characters to csid `0`.

## Dependencies

Uses Citrus stdenc templates, `_bcs` parsing helpers, `machine/endian.h`, and standard wide-character types.

## Risks And Invariants

- `current_endian` is per-state and transitions from unknown to BOM-detected or preferred endian.
- UTF-16 low-surrogate validation is required after a high surrogate.
- UTF-32 rejects surrogate code points but does not otherwise deeply validate Unicode scalar upper bounds beyond code representation.
