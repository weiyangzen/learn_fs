# sources/storage-engines/wiredtiger/src/btree/col_srch.c

## Purpose
`col_srch.c` searches variable-length column-store btrees by record number. It descends internal column pages, pins the target leaf, searches on-page variable-column cells and update/append skiplists, and positions `WT_CURSOR_BTREE` fields so reads and modifications know whether the match is on-page, inserted, before-page, or past-end.

## Important APIs, Types, And Functions
- `__wt_col_search` is the exported search routine.
- `__check_leaf_key_range` is a fast parent-range check when repositioning on a known leaf.
- It uses `__col_var_search`, `__col_var_last_recno`, `__col_insert_search`, `WT_COL_UPDATE_SLOT`, and `WT_COL_APPEND`.
- Key state lives in `WT_CURSOR_BTREE`: `ref`, `recno`, `slot`, `compare`, `ins_head`, `ins`, insert stacks, and flags such as `WT_CBT_VAR_ONPAGE_MATCH`, `WT_CBT_READ_ONCE`.

## Control Flow
The search clears cursor position state and maps `WT_RECNO_OOB` append searches to `UINT64_MAX` for descent. If the caller supplied a leaf, it may check the leaf's range using the ref's starting recno and the parent's next child starting recno; failure returns without a full tree search.

Full-tree search starts at the root and repeatedly binary-searches `WT_PAGE_COL_INT` page indexes to choose the child whose starting recno is the greatest lower bound of the target. The last slot has an append fast path with split-race detection. Child descent uses `__wt_page_swap` with restart support, and a split restart begins again at the root because the namespace may have moved above the current page.

On the leaf, `WT_RECNO_OOB` returns compare -1 without searching because allocation happens in modify. For normal recnos before the leaf start, it positions at slot 0 and compare 1. For on-page matches, it sets recno, slot, compare 0, marks `WT_CBT_VAR_ONPAGE_MATCH`, and then looks for an exact update-list insert. For past-end searches, it checks the append list first, then the last per-slot update list, and sets compare relative to the closest insert if found.

## State And Persistence Behavior
The routine does not persist data. It pins the selected leaf via page-swap/hazard-pointer behavior and prepares cursor state used by later reads or writes. It updates `btree->maximum_depth` when a deeper descent is observed.

## Dependencies And Integration Points
Column search integrates with internal page-index split generation, page swap/read code, variable-column on-page search helpers, column insert skiplist search, cursor flags, and column modification. Modification correctness depends on search stacks and compare values initialized here, especially for appends and per-slot update insertion.

## Risks
Split races during descent can misplace a search unless `WT_RESTART` and the last-slot descent race are handled correctly. Leaf-only repositioning depends on parent page-index hints that may be stale, so it validates the hint before using the next slot. Past-end behavior is subtle because append-list entries are closer than on-page last-record state, and cursor flags must indicate when an on-page value exists under an update list.

## Test Signals
Tests should search exact on-page records, exact update-list records, records before a leaf, records past a leaf/table end, append out-of-band recnos, leaf-only repositioning with safe and unsafe leaves, parent split races, stale `pindex_hint`, and read-once descent behavior. Follow-on modify tests are good signals because incorrect search stacks usually surface as insert serialization failures or misplaced updates.
