# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/listlist.c

Stores Word list definitions and tracks current numbering values.

Private structures:

- `list_desc_type`: list definition record with `list_block_type`, Word list ID, style ID, level, and next pointer.
- `list_value_type`: current numbering state for a list index and level.

Core state:

- `aulLfoList` / `usLfoLen`: Word 8+ LFO list ID mapping.
- `pAnchor` / `pBlockLast`: list definition linked list.
- `pValues`: active numbering values.
- `iOldListSeqNumber` / `usOldListValue`: legacy pre-Word-8 numbering state.

Key functions:

- `vDestroyListInfoList()` frees all list definition/state memory and resets counters.
- `vBuildLfoList()` parses the `pllfo` buffer into list IDs with sanity checks.
- `vAdd2ListInfoList()` appends list metadata and clamps invalid huge `ulStartAt` to `1`.
- `pGetListInfo()` maps list index and level to a `list_block_type`, with level-0 fallback.
- `pGetListInfoByIstd()` retrieves list metadata by style ID.
- `vRestartListValues()` deletes less-significant level counters after a higher-level increment when restart rules require it.
- `usGetListValue()` advances numbering for old and new list formats.

This module directly affects generated list numbers and indentation behavior during `word2text.c` output.
