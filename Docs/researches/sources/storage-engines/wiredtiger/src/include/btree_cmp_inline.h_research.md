<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/btree_cmp_inline.h -->
# sources/storage-engines/wiredtiger/src/include/btree_cmp_inline.h

## Purpose
Defines hot-path comparison helpers for WiredTiger B-tree searches, cursor bounds checks, and row-key comparisons. It provides bytewise lexicographic comparison, prefix-skipping comparison, optional application collator dispatch, and a short-key fast path.

## Important APIs, Types, and Functions
`__wt_lex_compare` compares two `WT_ITEM` byte strings and returns the usual negative/zero/positive ordering. It uses x86 SSE or ARM NEON 16-byte chunks when available, then finishes with scalar byte comparison and length tie-breaking.

`__wt_compare` wraps `__wt_lex_compare` unless a `WT_COLLATOR` is configured, in which case it calls `collator->compare`.

`__wt_compare_bounds` checks a cursor key or column-store record number against upper or lower cursor bounds. Row-store bounds use `__wt_compare`; column-store bounds unpack a record number with `__wt_struct_unpack`.

`__wt_lex_compare_skip` compares after an already-known common prefix tracked by `matchp`, updating `matchp` as additional equal bytes are observed. Diagnostic builds can recompute the full comparison under `WT_TIMING_STRESS_PREFIX_COMPARE`.

`__wt_compare_skip` combines the skip optimization with optional collator dispatch. Collated comparisons cannot use the prefix-skip optimization and delegate the full comparison.

`__wt_lex_compare_short` is an unrolled switch for keys up to `WT_COMPARE_SHORT_MAXLEN` (9 bytes), matching packed record-number key sizes.

## Control Flow
Large comparisons first align to vector-sized chunks: x86 uses aligned or unaligned loads depending on both pointer addresses; ARM NEON scans 16-byte vectors. Both variants stop at the first unequal vector and let scalar code identify the exact byte difference. Small comparisons skip vectorization and go straight to the scalar loop.

Bounds checks split on `upper`. For row-store, the comparison result is interpreted according to inclusive or exclusive cursor-bound flags. For column-store, the packed bound buffer is decoded into a `uint64_t recno` before the same inclusive/exclusive logic is applied.

## State and Persistence Behavior
This file does not own persistent state. It reads cursor bound buffers and B-tree collator configuration, increments `cursor_bounds_comparisons`, and updates the caller-owned `matchp` and `key_out_of_bounds` outputs. The correctness of `matchp` depends on callers only passing a prefix length known to match both keys.

## Dependencies and Integration Points
The helpers depend on `WT_ITEM`, `WT_SESSION_IMPL`, `WT_CURSOR`, `WT_COLLATOR`, `CUR2BT`, cursor bound flags, stat macros, vector intrinsics, and WiredTiger var-struct unpacking. They integrate with B-tree search/descent, cursor next/prev bound enforcement, row-store prefix-compressed key handling, and any table using a custom collator.

## Risks and Edge Cases
The vector paths must not read past `min(user_size, tree_size)`, so the code strips a remainder before vector scanning and restores it for scalar finish. `__wt_lex_compare_skip` computes `WT_MIN(usz, tsz) - *matchp`; callers must ensure `matchp` is no larger than the shorter key. Collator paths ignore `matchp`, so prefix optimization cannot be assumed for user-defined ordering. Column bounds rely on the raw bound buffer containing a valid packed `q` record number.

## Test Signals
Relevant test signals include row-store and column-store cursor-bound tests, custom-collator ordering tests, prefix-compressed row search tests, and architecture builds that exercise x86 intrinsics, ARM NEON, and scalar fallback. Diagnostic timing stress for prefix comparison is a direct consistency check between skip and full comparison paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/btree_cmp_inline.h -->
