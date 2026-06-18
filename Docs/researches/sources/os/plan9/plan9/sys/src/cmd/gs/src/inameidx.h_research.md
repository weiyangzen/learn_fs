# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/inameidx.h

Name index constants and count/index permutation support for Ghostscript names.

Key behavior:
- Includes `gconfigv.h` for `EXTEND_NAMES`, defaulting it to `0`.
- Defines sub-table dimensions: `NT_LOG2_SUB_SIZE`, `NT_SUB_SIZE`, and `NT_SUB_INDEX_MASK`.
- Reserves initial entries for unused index 0, empty name, and 128 one-character names.
- Provides `NT_1CHAR_NAMES_DATA`, the initial one-byte-name data table.
- Defines `name_count_to_index` and `name_index_to_count` permutations so name allocation order is scrambled within sub-tables.

Research notes:
- The permutation factor is 23, with reverse factor 1959 for power-of-two sub-table sizes up to 4096.
- The comments explain the performance motivation: dictionary lookup benefits because it does not need to scramble separately.
