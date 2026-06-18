# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/btree.c

## Role

Generic XFS scrub btree walker. It validates structural consistency for regular XFS btrees, including pointer validity, record/key ordering, sibling links, parent key coverage, minimum record counts, buffer verifier results, and ownership cross-references.

## Key Functions

- `xchk_btree()` performs a depth-first traversal of all btree levels and dispatches each leaf record to a caller-provided scrub callback.
- `xchk_btree_rec()` checks global record ordering and verifies leaf records fit under parent low/high keys.
- `xchk_btree_key()` checks node key ordering and parent key bounds.
- `xchk_btree_get_block()` loads a btree block, runs verifier checks, rechecks buffers, validates minrecs, ownership, sibling pointers, and parent keys.
- `xchk_btree_block_check_sibling()` and `xchk_btree_block_check_siblings()` verify left/right sibling links against adjacent parent pointers.
- `xchk_btree_check_owner()` cross-references btree blocks against used-space and rmap ownership data; bnobt/rmapbt self-checks are deferred to avoid cursor conflicts.
- `xchk_btree_process_error()` and `xchk_btree_xref_process_error()` translate btree operation errors into scrub outcome flags.

## Research Notes

The walker treats verifier failures as metadata corruption flags rather than fatal returns, allowing scrub to report bad structures cleanly. It has special handling for inode-rooted btrees, overlapping-key btrees, and historical data-fork bmap root spill behavior.
