# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/jis.h

## Purpose
Provides macro helpers for converting between JIS X 0208 byte pairs and Microsoft Shift-JIS byte pairs, plus byte-range predicates used by the Japanese converters.

## Key Elements
Defines in-place transformation macros:
- `J2S(_h, _l)`: mutates a valid JIS X 0208 high/low byte pair into Shift-JIS form, including the Shift-JIS skipped byte ranges.
- `S2J(_h, _l)`: mutates a valid Shift-JIS pair into JIS X 0208 form.
- `ISJKANA(_b)`: detects JIS X 0201 katakana range `0xa0..0xdf`.
- `CANS2JH`, `CANS2JL`, `CANS2J`: validate Shift-JIS lead/trail bytes before conversion.
- `CANJ2SB`, `CANJ2S`: validate 94-character-set JIS bytes.

## Dependencies
Included by `conv_jis.c`, which uses `CANS2J`/`S2J` to parse Shift-JIS and mixed JIS input, and `J2S` to emit Shift-JIS output from kuten table indexes.

## Behavior/Risks
The transform macros mutate their arguments multiple times and assume simple lvalue integer variables. Passing expressions with side effects would be unsafe. The comments state callers must pass bytes already in valid range; the range predicates are separate and must be used by callers before conversion.

The macros operate on arithmetic byte values, not typed `uchar *` despite the comments saying pointer-like names. They are compact and old-style, so misuse can produce subtle conversion errors.

## Verification
Read completely: 107 lines, 2873 bytes. SHA-256: `b6d54e880597d35bc4971dd8ceb89073028b357591c6e4ab2899a314b172db9b`.
