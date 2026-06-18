# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf7.c

## Scope

Implements the Citrus ctype/stdenc module for UTF-7, including direct characters, base64 shifted sequences, UTF-16 unit conversion, and state reset output.

## APIs And Behavior

- Maintains shift/base64 state in `_UTF7State`.
- `_citrus_UTF7_mbrtowc_priv()` decodes direct bytes and shifted base64 sequences, using UTF-16 intermediate units and surrogate-pair handling.
- `_citrus_UTF7_wcrtomb_priv()` emits direct characters when permitted, `+-` for literal plus, or shifted base64 sequences for encoded characters.
- `_citrus_UTF7_put_state_reset()` terminates an open shifted sequence when necessary.
- Stdenc maps all decoded characters into csid `0` and reports incomplete character/shift state.

## Dependencies

Uses Citrus ctype/stdenc templates, base64 helper logic internal to the file, and wide-character/errno APIs.

## Risks And Invariants

- UTF-7 is state-dependent; reset output is required to close shifted mode.
- Base64 bit-buffer accounting must preserve partial bits across calls.
- Surrogate handling must reject malformed high/low pairs while still supporting restart on incomplete input.
