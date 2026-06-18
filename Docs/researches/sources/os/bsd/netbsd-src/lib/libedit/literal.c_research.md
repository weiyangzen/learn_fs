# File Research: sources/os/bsd/netbsd-src/lib/libedit/literal.c

## Purpose
Handles display-time literal escape sequences that need to be emitted as encoded byte strings while occupying the screen width of a single visible wide character.

## Main Interfaces
- `literal_init`: zeroes per-line literal storage.
- `literal_end`: clears storage at teardown.
- `literal_clear`: frees all saved literal byte strings.
- `literal_add`: encodes a literal sequence, stores it, and returns an `EL_LITERAL` sentinel value containing the storage index.
- `literal_get`: resolves an `EL_LITERAL` sentinel back to the saved byte string.

## Control Flow
`literal_add` computes the display width of the visible character, encodes the preceding literal sequence plus visible character with `ct_encode_char`, stores the resulting byte string in a growable array, and returns a tagged `wint_t`. Refresh output later recognizes the tag and emits the saved bytes.

## Dependencies
Uses `wcwidth`, `ct_enc_width`, `ct_encode_char`, and libedit allocation helpers from `el.h`.

## Risks And Notes
- `literal_get` uses assertions and assumes the caller passes a valid tagged index from the current literal table.
- `literal_clear` is called during refresh; saved sentinels are only meaningful for the active render pass.
