# File Research: sources/os/linux/linux-stable/fs/ubifs/log.c

## Role

Implements UBIFS log manipulation. The log is the fixed flash area that records references to journal bud LEBs and commit-start nodes. It contains no file data itself, but defines what bud data must be replayed or indexed.

## Bud Lookup and Accounting

`ubifs_search_bud()` finds a bud by LEB number in the buds rb-tree.

`ubifs_get_wbuf()` maps a bud LEB to the write-buffer of its journal head.

`ubifs_add_bud()` inserts a bud into the rb-tree and journal-head list and increases `c->bud_bytes` by the bud’s addressable tail. This accounting is intentionally done before data is written so mount-time scanning remains bounded by bud references.

`dbg_check_bud_bytes()` verifies debug accounting by summing journal-head bud lists.

## Adding Buds to the Log

`ubifs_add_bud_to_log()` writes a `UBIFS_REF_NODE` for a new bud:

- Locks `log_mutex`.
- Ensures enough empty log space remains for future commit.
- Ensures total bud bytes do not exceed `c->max_bud_bytes`.
- Requests background commit when bud bytes pass the background threshold.
- Advances or unmaps log head LEBs as needed.
- Maps empty bud LEBs before referencing them to avoid recovery seeing garbage after power loss.
- Writes the ref node and updates log authentication hash state.
- Adds the bud to in-memory tracking.

It returns `-EAGAIN` when commit is required rather than treating log fullness as fatal.

## Commit Start and End

`ubifs_log_start_commit()` writes a commit-start node plus ref nodes for still-open journal heads in one min-I/O-aligned write to a fresh log LEB. It resets the log hash, copies hash state to journal heads, advances the log head, removes closed buds from active tracking, and sets `min_log_bytes` to zero so writers can use remaining log during commit.

`remove_buds()` preserves open buds by moving their start offset forward to the current wbuf offset and moves closed buds to `old_buds` until post-commit.

`ubifs_log_end_commit()` moves the log tail to the commit-start LEB, restores `min_log_bytes` to one LEB, subtracts committed bud bytes, checks accounting, and writes the master node.

`ubifs_log_post_commit()` returns old buds to lprops and unmaps obsolete log LEBs only after commit completion, preserving recovery safety if commit fails.

## Log Consolidation

`ubifs_consolidate_log()` rewrites the log after repeated failed commits may have left it too full. It scans from tail to head, keeps only the first commit-start node and non-duplicate ref nodes, writes compacted nodes with padding, unmaps remaining log LEBs, and updates the log head.

The helper `done_already()` tracks duplicate ref LEBs in an rb-tree.

## Research Notes

This file enforces journal size bounds and recovery ordering. It is the point where journal head allocation in `journal.c` becomes persistent, and where commit transforms active buds into indexed file-system state while keeping enough old state for replay.
