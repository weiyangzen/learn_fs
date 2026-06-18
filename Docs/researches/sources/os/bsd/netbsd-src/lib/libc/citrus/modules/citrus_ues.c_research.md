# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_ues.c

## Scope

Implements the Citrus ctype/stdenc module for Unicode escape sequences, supporting Java-style `\uXXXX` behavior and optional C99 `\UXXXXXXXX` behavior.

## APIs And Behavior

- State buffers up to 12 bytes, enough for surrogate-pair escape output.
- `_citrus_UES_mbrtowc_priv()` decodes raw/basic characters and escape sequences, handles incomplete escape state, and combines surrogate pairs in non-C99 mode.
- `_citrus_UES_wcrtomb_priv()` emits raw characters, `\uXXXX`, surrogate-pair `\uXXXX\uXXXX`, or C99 `\UXXXXXXXX` forms depending on mode and code point.
- Stdenc maps all valid characters into csid `0`.
- Module init parses `C99` from the variable string and sets `mb_cur_max` to 10 or 12.

## Dependencies

Uses Citrus ctype/stdenc templates, `_bcs` case-insensitive parsing, `wchar_t`, and errno conventions.

## Risks And Invariants

- C99 mode changes both accepted escape syntax and what counts as a basic unescaped character.
- Surrogates are rejected as standalone scalar values in C99 mode but are used internally for non-C99 surrogate-pair decoding.
- Restart handling depends on preserving partially-read escape bytes in `_UESState`.
