# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/inameidx.h

Ghostscript name-index configuration header. It defines how name counts map to physical name-table indices and how the name table is partitioned into subtables.

Key contents:
- Includes `gconfigv.h` for `EXTEND_NAMES` and defaults it to `0`.
- Defines `NT_LOG2_SUB_SIZE`, `NT_SUB_SIZE`, and `NT_SUB_INDEX_MASK`, scaling subtable size with extended-name mode.
- Reserves entry 0, entry 1 for the zero-length name, and entries 2 through 129 for 128 one-character names.
- Defines `NT_1CHAR_NAMES_DATA`, the static one-character name initialization data.
- Defines `name_count_to_index`, which scrambles allocation count order within a subtable using factor `23`.
- Defines the unused inverse mapping `name_index_to_count` with factor `1959`.

Notable dependencies:
- `gconfigv.h`.

Research notes:
- The count-to-index permutation is designed to avoid separate hash scrambling during dictionary lookup.
- The permutation preserves the subtable portion of the index and only permutes the low subtable index bits.
- The inverse factor comment says it works for `NT_SUB_SIZE` values up to 4096, but the inverse macro is not currently used.
