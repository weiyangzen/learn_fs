# sources/storage-engines/wiredtiger/src/conn/api_calc_modify.c

## Purpose

`api_calc_modify.c` implements WiredTiger's helper for representing a full value update as a compact list of `WT_MODIFY` operations. It compares an old byte string and a new byte string, finds large common regions, and emits replacement spans for the differing regions when the result fits caller-provided limits.

## Important APIs, Types, and Functions

- `wiredtiger_calc_modify`: public API wrapper accepting `WT_SESSION *`.
- `__wt_calc_modify`: internal implementation accepting `WT_SESSION_IMPL *`.
- `WT_MODIFY`: output entry containing target offset, old span size, and replacement bytes.
- `WT_CM_STATE`: local comparison state including old/new ranges, consumed pointers, max diff budget, and max entry count.
- `WT_CM_MATCH`: local match result with old pointer, new pointer, and match length.
- `__cm_fingerprint`: reads an 8-byte block as a hash-like fingerprint.
- `__cm_extend`: expands a candidate match forward and backward to its maximal equal byte span.
- `__cm_add_modify`: appends one `WT_MODIFY` and advances budget accounting.

## Control Flow

`__wt_calc_modify` rejects inputs shorter than `WT_CM_MINMATCH` because short values are not worth delta encoding. It initializes comparison state and treats `*nentriesp` as input capacity, then resets it to the output count. It first trims matching prefixes and suffixes using `__cm_extend`. If the remaining middle is too small for block matching, it emits one trailing replacement.

For the middle diff, it scans the new value one byte at a time while maintaining two fingerprint markers in the old value separated by a growing gap. When the new-side fingerprint matches either old-side marker, `__cm_extend` verifies and expands the match. A match shorter than `WT_CM_MINMATCH` is ignored. A useful match causes `__cm_add_modify` to emit the replacement bytes between the last consumed positions and the match, then the scan restarts after the matched region. At the end, any remaining old or new bytes are emitted as a final modify.

## State and Persistence Behavior

The algorithm is stateless outside the caller-provided output array. `WT_MODIFY.data.data` points into `newv->data`, so the new value memory must remain valid while the modify list is consumed. No database state is read or persisted. `maxdiff` is consumed as replacement bytes are emitted, and `*nentriesp` is rewritten to the number of generated entries.

## Dependencies and Integration Points

The file depends on internal utility macros and functions from `wt_internal.h`, including `WT_RET`, `WT_ASSERT`, `WT_MIN`, and error code conventions. It integrates with update paths that can store or transmit modify records rather than full values, and the public `wiredtiger_calc_modify` entry allows callers to request the same calculation from a `WT_SESSION`.

## Risks and Edge Cases

- `__cm_fingerprint` copies 8 bytes with `memcpy`; callers rely on prior bounds checks ensuring at least `WT_CM_BLOCKSIZE` bytes are readable.
- The function returns `WT_NOTFOUND` when the diff cannot fit `maxentries` or `maxdiff`, or when growing gap search exceeds the diff budget.
- `WT_MODIFY` entries borrow memory from `newv`; misuse after freeing or changing `newv` is unsafe.
- Matching is heuristic rather than a full optimal diff. It favors speed and compact-enough deltas over minimal edit scripts.
- The gap doubling logic can bail out on large shifts even when a possible diff exists, which is acceptable because callers can fall back to a full update.

## Test Signals

Unit tests should cover unchanged values, prefix/suffix-only changes, insertions, deletions, replacements, too-small inputs, max entry exhaustion, max diff exhaustion, and reconstruction of `newv` from `oldv` plus generated modifies. Fuzz or randomized differential tests are valuable: generate old/new byte arrays, call `__wt_calc_modify`, apply returned modifies, and assert exact reconstruction or an allowed `WT_NOTFOUND` fallback.
