# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tables.c

This file defines static MPEG Layer III Huffman and MPEG version tables used by bit counting, bitstream writing, and parameter initialization.

Key responsibilities:
- Defines Huffman codeword tables `t1HB` through `t33HB`.
- Defines Huffman code-length tables `t1l` through `t33l`.
- Defines the public `ht[HTN]` array of `struct huffcodetab` entries.
- Defines packed bit-count helper tables:
  - `largetbl` for comparing table 16 and 24 style choices.
  - `table23` for comparing Huffman tables 2 and 3.
  - `table56` for comparing Huffman tables 5 and 6.
- Defines MPEG bitrate/samplerate/version/header constants:
  - `bitrate_table`
  - `samplerate_table`
  - `version_string`
  - `header_word`

Integration:
- `takehiro.c` uses `ht`, `t32l`, `t33l`, `largetbl`, `table23`, and `table56` for Huffman table selection and bit counting.
- Encoder initialization and bitstream formatting use bitrate/samplerate/header constants.

Dependencies:
- Includes `util.h` and `tables.h`.

Notable behavior:
- The `ht` table maps table numbers `0..33`, with unused entries represented by null table pointers or length-only entries.
- Tables 16 through 23 share the same code table with increasing `linmax`.
- Tables 24 through 31 share another large-value table family.
- Count1 tables 32 and 33 encode quadruples.

Risks and edge cases:
- These constants encode MPEG spec data; any table corruption changes bitstream validity.
- Some generated helper tables pack two candidate bit counts into one `unsigned int` for fast comparison, so endian-independent arithmetic assumptions matter only at integer value level, not byte layout.
- The file comment says `end of tables.h` at the end, but this is harmless stale text.
