# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf8.c

## Scope

Implements the Citrus ctype/stdenc module for UTF-8, including restartable multibyte decoding and wide-character encoding.

## APIs And Behavior

- Builds a byte-class/count table for UTF-8 sequence lengths.
- `_citrus_UTF8_mbrtowc_priv()` buffers partial sequences, determines expected length from the leading byte, validates continuation bytes, and produces a wide character.
- `_citrus_UTF8_wcrtomb_priv()` emits UTF-8 for wide characters up to the module’s supported range.
- Stdenc maps wide characters to csid `0`.
- State descriptor reports initial state when no bytes are buffered, otherwise incomplete character.

## Dependencies

Uses Citrus ctype/stdenc templates and standard wide-character/errno support.

## Risks And Invariants

- Correct restart behavior depends on retaining `chlen`, expected length, and accumulated bytes.
- Continuation-byte validation and overlong/invalid sequence handling are correctness-sensitive.
- `MB_CUR_MAX` is fixed at 6 for historical UTF-8 coverage, wider than modern Unicode scalar UTF-8.
