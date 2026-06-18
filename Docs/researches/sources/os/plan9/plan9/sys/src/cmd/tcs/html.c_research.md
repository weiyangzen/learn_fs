# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/html.c

This file implements the `html` input and output converter for `tcs`, translating between HTML character references/entities and Plan 9 runes.

Key behavior:
- Defines `Hchar { char *s; Rune r; }` and a static `byname[]` table of named HTML entities mapped to rune values.
- Uses leading `_` in entity names to mean "recognize this spelling on input, but do not generate it on output"; examples include common nonstandard aliases.
- `html_init()` copies `byname` to `byrune`, strips leading underscores for input lookup, suppresses those entries from output generation by setting their `byrune` rune to `Runeerror`, and sorts both lookup arrays.
- `findbyname()` binary-searches entity names to decode `&name;`.
- `findbyrune()` binary-searches rune values to choose a named entity for output.
- `html_in()` reads UTF input with `Bgetrune()`, recognizes `&name;`, decimal numeric references, and lowercase hexadecimal numeric references beginning `&#x`, then emits runes through `OUT`.
- `html_out()` writes ASCII runes directly, emits known non-ASCII runes as named entities, and falls back to decimal numeric references for other non-ASCII runes.

Important details:
- The comment says `&lt;`, `&gt;`, `&quot;`, and `&amp;` are intentionally omitted, but the table still includes `lt`, `gt`, `quot`, and `amp`; output behavior is governed by the sorted `byrune` table and ASCII fast path, so ASCII `<`, `>`, `"`, and `&` are written directly.
- Input entity scanning stops on semicolon or whitespace and uses a 100-byte buffer; malformed or unknown references are copied through as literal UTF text.
- Numeric reference parsing requires the final semicolon to remain present after `strtol`; out-of-range or negative values are treated as bad references and copied literally.
- Output uses `Biobuf` because generated entity strings can exceed the normal UTF bytes-per-rune size.
- `html_out()` initializes a new `Biobuf` on fd 1 for each call and flushes at the end of the batch.

Filesystem relevance:
- Indirect: converts HTML-encoded text in files or streams; no filesystem APIs beyond standard fd-based I/O.
