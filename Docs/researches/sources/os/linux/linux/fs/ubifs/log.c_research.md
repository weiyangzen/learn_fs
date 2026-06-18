# File Research: sources/os/linux/linux/fs/ubifs/log.c

## Purpose

`log.c` manages the UBIFS journal log: the fixed flash area containing commit-start nodes and reference nodes for bud LEBs. It maintains the in-memory bud tree/list state, enforces log and journal size limits, starts and finishes commit log transitions, releases old buds after commit, and can consolidate the log after failed commits.

## Bud Lookup and Registration

`ubifs_search_bud()` searches the red-black tree of buds by LEB number under `buds_lock`. `ubifs_get_wbuf()` finds the journal head write-buffer associated with a bud LEB. `ubifs_add_bud()` inserts a bud into the tree, links it to its journal head list when heads are initialized, and increases `c->bud_bytes` by the bud's remaining LEB span. This accounting bounds mount-time journal replay.

## Adding Buds to the Log

`ubifs_add_bud_to_log()` allocates a bud and ref node, locks `log_mutex`, checks read-only error state, ensures enough empty log bytes remain for the next commit, enforces `max_bud_bytes`, optionally requests background commit after `bg_bud_bytes`, prepares a ref node, unmaps a fresh log LEB when needed, maps empty bud LEBs before referencing them, writes the ref node with `ubifs_write_node()`, updates authentication hash state, advances the log head, and inserts the bud. It returns `-EAGAIN` when log or journal size pressure requires commit.

## Commit Log Lifecycle

`remove_buds()` runs during commit start. It preserves buds still pointed to by active journal heads by advancing their starts to the current write-buffer offsets; closed buds are removed from the active tree and moved to `old_buds` so recovery can still replay them if commit fails.

`ubifs_log_start_commit()` writes a commit-start node plus ref nodes for active journal heads into a fresh log LEB in one write. It resets the log hash, pads to min-I/O size, updates the log head offset, calls `remove_buds()`, and temporarily drops `min_log_bytes` so writers can use log space while commit continues.

`ubifs_log_end_commit()` moves the log tail to the new commit-start LEB, restores `min_log_bytes` to one LEB so the next commit is guaranteed, subtracts committed bud bytes from `bud_bytes`, checks debug accounting, and writes the master node.

`ubifs_log_post_commit()` finally returns old bud LEBs to lprops and unmaps old log LEBs from the previous tail up to the new tail. This delayed release preserves recovery data until commit is fully durable.

## Log Consolidation

`ubifs_consolidate_log()` handles recovery cases where repeated failed commits leave the log too full for another commit. It scans from tail to head, copies only the first commit-start node and unique reference nodes into compacted log LEBs, writes padded LEB images via `ubifs_leb_change()`, unmaps no-longer-used log LEBs, and updates the log head. `done_already()` tracks duplicate referenced LEBs in an rb-tree, and `add_node()` handles LEB-boundary padding and writing.

## Invariants

Log writes are serialized by `log_mutex` except during the exclusive commit-start phase. `bud_bytes` must match the sum of active head bud spans; `dbg_check_bud_bytes()` verifies this under debug checking. Empty bud LEBs are mapped before the log references them to avoid recovery seeing stale physical contents after an unclean reboot.
