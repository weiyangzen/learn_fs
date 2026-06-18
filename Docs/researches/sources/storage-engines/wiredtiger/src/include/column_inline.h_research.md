<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/column_inline.h -->
# sources/storage-engines/wiredtiger/src/include/column_inline.h

## Purpose
Defines inline search helpers for column-store insert skiplists and variable-length column-store page slots. These helpers support exact and directional record-number lookups, insert-position stack construction, append detection, and RLE-aware page indexing.

## Important APIs, Types, and Functions
`__col_insert_search_gt` returns the smallest inserted record greater than a target recno. `__col_insert_search_lt` returns the largest inserted record smaller than a target recno. `__col_insert_search_match` returns an exact recno match.

`__col_insert_search` performs the general insert-list search and fills `ins_stack` and `next_stack` for insertion at each skiplist level. It fast-paths appends at or beyond the current last record.

`__col_var_last_recno` computes the last base record on a variable-length column-store page, accounting for run-length encoded repeats but ignoring append-list inserts.

`__col_var_search` maps a recno to a `WT_COL` slot using a binary search over repeat metadata followed by direct offset arithmetic.

## Control Flow
Skiplist searches start from the highest level and move forward while the next record is below or at the target condition, then drop levels. Acquire barriers guard against compiler and weak-memory reordering while reading concurrently updated skiplist links. Directional searches use first/last fast paths to avoid full skiplist traversal when the target lies outside the list.

`__col_insert_search` fills insertion predecessor and successor arrays while descending. On append, it points stack entries at tails or heads and sets `next_stack` to null. On exact match, it fills lower-level stacks from the matched node's next links.

Variable-column search first binary-searches `pg_var_repeats` for an RLE run containing the recno. If no run contains it, it starts after the largest repeat less than the target and computes the slot offset while avoiding arithmetic overflow.

## State and Persistence Behavior
The skiplist helpers read volatile in-memory insert lists (`WT_INSERT_HEAD` and `WT_INSERT`) that represent updates not necessarily present in the base disk image. `__col_var_search` reads in-memory page structures derived from persistent column-store cells and repeat metadata. No persistent state is written here.

## Dependencies and Integration Points
Depends on `WT_INSERT`, `WT_INSERT_HEAD`, skiplist macros, `WT_INSERT_RECNO`, `WT_COL`, `WT_COL_RLE`, page type fields, record-number constants, and memory barrier macros. It integrates with column-store cursor search/next/prev, append handling, update insertion, reconciliation of column pages, and visible update selection.

## Risks and Edge Cases
Concurrent insertions can reorder observations across skiplist levels without barriers; the code explicitly guards against stale lower-level values causing missed records. Directional searches assume the existence checks against first/last remain valid enough under concurrent mutation. Variable-column last-recno and search must handle empty pages, pages with no repeats, repeated runs, appended records outside the base page, and overflow-safe recno arithmetic near `UINT64_MAX`.

## Test Signals
Useful tests include fixed and variable column-store cursor search/next/prev, concurrent append/update workloads, exact and non-exact recno searches, RLE-heavy pages, empty pages, append-list interactions, and sanitizer/TSAN runs around skiplist memory ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/column_inline.h -->
