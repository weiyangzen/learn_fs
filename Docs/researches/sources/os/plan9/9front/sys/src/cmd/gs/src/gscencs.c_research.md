# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscencs.c

## Role

`gscencs.c` implements lookup operations over the compact built-in encoding data from `gscedata.c`.

This is font encoding logic, not filesystem code.

## Main Public Symbols

- `gs_c_min_std_encoding_glyph`
- `gs_c_known_encode(gs_char ch, int ei)`
- `gs_c_decode(gs_glyph glyph, int ei)`
- `gs_c_glyph_name(gs_glyph glyph, gs_const_string *pstr)`
- `gs_is_c_glyph_name(const byte *str, uint len)`
- `gs_c_name_glyph(const byte *str, uint len)`

## Encoding Scheme

- `gs_c_min_std_encoding_glyph` is `gs_min_cid_glyph - 0x10000`.
- Built-in encoding glyph IDs are stored as this base plus the compact `N(len, offset)` value from `gscedata.c`.
- These private glyph values are only intended for use with `gs_c_glyph_name` or `gs_c_decode`.

## Function Behavior

- `gs_c_known_encode`:
  - validates encoding index and character range
  - returns `gs_no_glyph` for invalid input
  - otherwise returns private glyph value
- `gs_c_decode`:
  - binary-searches the reverse table for the requested encoding
  - returns the character code on match
  - returns `GS_NO_CHAR` on miss
- `gs_c_glyph_name`:
  - decodes packed length and offset
  - returns a string slice into `gs_c_known_encoding_chars`
  - debug builds perform range checks
- `gs_is_c_glyph_name`:
  - tests whether a string pointer lies inside the generated glyph-name character pool
- `gs_c_name_glyph`:
  - binary-searches the glyph-name pool for a name of a given length
  - returns the private glyph code or `gs_no_glyph`

## Test Code

Under `#ifdef TEST`, the file includes a standalone test program that checks sample glyphs such as `caron`, `carriagereturn`, `circlemultiply`, `numbersign`, and reverse lookup behavior.

## Dependencies

- Includes `memory_.h`, `gscedata.h`, `gscencs.h`, `gserror.h`, and `gserrors.h`.
- Uses `memcmp`, Ghostscript string types, and Ghostscript error handling.

## Notable Risks

- `gs_c_decode` assumes `ei` is valid; unlike `gs_c_known_encode`, it does not range-check the encoding index.
- `gs_c_glyph_name` only validates packed glyph values in debug builds.
- `gs_is_c_glyph_name` checks pointer range but does not validate `len` against the end of the character pool.
