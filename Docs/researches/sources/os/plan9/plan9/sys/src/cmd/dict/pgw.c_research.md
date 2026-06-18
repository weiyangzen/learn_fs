# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/pgw.c

Implements the Project Gutenberg Webster dictionary backend. Its structure is a lighter variant of `oed.c`: SGML-like tags, entity decoding, translation tables, and callbacks `pgwprintentry`, `pgwnextoff`, and `pgwprintkey`.

The file defines tag and special-character tables for Webster markup, normal/Greek/subscript/superscript byte translation tables, and parser state for current tag and entity. Entities are parsed with `getspec`, ending at `;`, unlike OED’s `.` terminator.

`pgwprintentry` streams entries with optional raw and headword-only modes. It decodes text through `normtab`, combines accent entities with buffered previous runes, expands multi-rune entities, handles paragraph sentinel `PAR`, and reacts to tags such as `hw`, `sn`, `p`, `col`, `blockquote`, and `u` for headword selection, sense breaks, paragraph breaks, and a slash marker.

`pgwnextoff` scans for Webster entry starts, normally `<p><hw>`, with a fallback path for `<p>{...`. `pgwprintkey` reuses a built-in OED-like pronunciation key.

Integration points: registered by `utils.c` as `pgw` with `/lib/dict/pgw` and `/lib/dict/pgwindex`.

Risks and notes: like `oed.c`, it is a permissive hand parser with fixed buffers and approximation-heavy entity translation. Formatting is flattened to plain text; table/block styling becomes simple line breaks.
