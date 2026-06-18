# File Research: sources/os/linux/linux/fs/nls/mac-inuit.c

Implements the `macinuit` NLS codepage module.

Key behavior:
- Provides generated mappings for a Mac Inuit charset centered on Canadian Aboriginal Syllabics.
- The extended byte range maps heavily into Unicode pages `14`, `15`, and `16`, with some Latin, punctuation, and symbol entries.
- Reverse lookup is sparse through pages `00`, `01`, `14`, `15`, `16`, `20`, and `21`.
- Uses the common one-byte conversion callbacks:
  - `char2uni()` maps one byte to one Unicode value.
  - `uni2char()` maps one Unicode value to one byte only when the reverse table has an exact entry.
- Registers charset name `macinuit`.

Important interactions:
- The generated lower/upper tables are unusual: broad placeholder-style values dominate rather than normal ASCII-style case folding.
- Consumers should treat this module primarily as exact charset conversion data.
