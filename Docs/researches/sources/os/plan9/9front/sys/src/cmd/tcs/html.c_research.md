# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/html.c

## Purpose
Implements the `tcs` HTML character reference codec. It converts HTML named and numeric character references to Plan 9 `Rune` values on input and emits non-ASCII runes as HTML entities or decimal numeric references on output.

## Key Elements
Defines `Hchar { char *s; Rune r; }` and a 2004-entry `byname[]` table of HTML entity names to Unicode scalar values. Names beginning with `_` are accepted after stripping the underscore but are not generated.

Runtime lookup is initialized by `html_init()`, which copies `byname` into `byrune`, sorts by name for input lookup, sorts by rune for output lookup, suppresses nonstandard names for generation, and resolves duplicate entity names for the same rune by keeping the shortest generated name. The file has 440 duplicate rune values in the entity table, so this duplicate-elimination step is central to stable output.

Functions:
- `hnamecmp`, `hrunecmp`, `hlencmp`: `qsort` comparators for name, rune, and name length.
- `html_init`: one-time table normalization and sorting.
- `findbyname`: binary-searches named references.
- `findbyrune`: binary-searches generated entity names by rune.
- `html_in`: reads UTF input through `Biobuf`, decodes `&name;`, `&#decimal;`, and `&#xhex;` forms, preserves invalid references literally, and calls `fixsurrogate`.
- `html_out`: writes ASCII runes raw, non-ASCII runes as named entities when available, otherwise as `&#decimal;`.

## Dependencies
Uses Plan 9 headers `u.h`, `libc.h`, `bio.h`, plus local `hdr.h` and `conv.h`. It depends on global conversion buffers/macros such as `runes`, `N`, `OUT`, `Runeerror`, `Runeself`, and `fixsurrogate`. `tcs.c` registers this file through two `convert[]` entries named `html`, one for `html_in` and one for `html_out`.

## Behavior/Risks
Input decoding intentionally refuses to turn references for ASCII syntax characters `<`, `>`, `&`, `"`, and `'` into raw characters; when a reference resolves to one of those characters, it re-emits the original reference text instead. This avoids introducing literal HTML syntax during "from HTML" conversion.

Malformed references are not dropped: the parser emits the original buffered bytes and preserves a consumed semicolon when present. Numeric references reject trailing garbage and negative values, but do not otherwise validate Unicode scalar range before assigning to `Rune`.

`html_out` only escapes non-ASCII runes. ASCII `<`, `>`, `&`, quotes, and apostrophes are written raw, so this is an encoding converter, not a general HTML escaper.

## Verification
Read completely: 2246 lines, 43604 bytes. SHA-256: `aaef031586249c31c6f07709993a1088c57dc3218018396f2a14181bcd1866f7`.
