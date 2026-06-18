# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tables.h

This header declares MPEG Layer III table structures and public table symbols.

Key definitions:
- `type1_t`, `type2_t`, `type34_t`, `type5_t`: older psychoacoustic table record types.
- `HTN`: Huffman table count, set to 34.
- `struct huffcodetab`: Huffman table descriptor with `xlen`, `linmax`, code table, and code-length table.

Exports:
- `table5[6]`: declared but not defined in `tables.c`; likely legacy/unused in this import.
- `ht[HTN]`
- `t32l[]`, `t33l[]`
- `largetbl[16*16]`
- `table23[3*3]`
- `table56[4*4]`

Dependencies:
- Includes `machine.h` for `size_t` and platform definitions.

Integration:
- Used by `takehiro.c` for Huffman bit counting.
- Used by `tables.c` to define the exported table data.

Risks and edge cases:
- `bitrate_table`, `samplerate_table`, `version_string`, and `header_word` are defined in `tables.c` but are not declared here; other declarations likely live in another common header.
- `table5` is declared here but absent from the read `tables.c`, suggesting dead legacy API or another definition elsewhere.
