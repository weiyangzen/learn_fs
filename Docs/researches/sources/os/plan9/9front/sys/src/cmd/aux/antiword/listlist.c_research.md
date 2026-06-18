# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/listlist.c

This file stores Word list/numbering definitions and tracks current list numbering values.

Key routines:
- `vDestroyListInfoList()` frees LFO entries, list description records, and active numbering values.
- `vBuildLfoList(...)` extracts list IDs from the Word 8+ LFO list.
- `vAdd2ListInfoList(...)` appends a list-level definition and clamps invalid starts.
- `pGetListInfo(...)` resolves a list block by list index and level, falling back to level 0.
- `pGetListInfoByIstd(...)` resolves list info by style id.
- `vRestartListValues(...)` clears less-significant list levels.
- `usGetListValue(...)` increments or initializes numbering for old and new Word list models.

Important behavior:
- Word 8+ numbering uses `usListIndex`, `ucListLevel`, LFO IDs, and per-level value records.
- Word versions before 8 use a simpler sequence counter with pause/start behavior.
- Restart behavior deletes deeper list-level counters unless `bNoRestart` is set.

Dependencies:
- Style blocks, numbering type helpers, Word list constants, allocation helpers.

Role in antiword:
- Provides numbering state for list paragraph rendering.
