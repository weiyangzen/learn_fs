# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/split.rs

## Purpose
Implements raftstore-v2 batch split: split checks, split request handling, apply-time physical tablet checkpointing, parent peer metadata updates, and initialization of new split peers.

## Important APIs, Types, And Functions
`SplitResult` returns the new regions, derived-region index, tablet index, size sharing flag, and new derived tablet. `SplitInit` carries a new region snapshot, inherited locks, metrics, and derived-leader hints. `RequestSplit`, `RequestHalfSplit`, `SplitFlowControl`, `SplitPendingAppend`, `temp_split_path`, and `report_split_init_finish` support scheduling and initialization. Main methods include `on_split_region_check`, `on_request_split`, `on_request_half_split`, `propose_split`, `apply_batch_split`, `on_apply_res_split`, `on_split_init`, `post_split_init`, `on_split_init_finish`, and `on_tablet_trimmed`.

## Control Flow
Leaders schedule split checks when approximate size/key updates or apply size deltas exceed thresholds, unless snapshot generation or busy split-check workers defer work. Manual split requests validate leadership, clean tablet state, disk-full policy, epoch, and key ordering before asking PD for split ids. Applying batch split validates requests, computes region boundaries and epochs, flushes existing writes, checkpoints the current tablet for all child regions and the derived parent tablet, opens the derived tablet, and updates apply-side region state. Peer apply result splits in-memory pessimistic locks, updates store metadata/read tablet under lock, tombstones the previous tablet, trims dirty data asynchronously, notifies PD, sends `SplitInit` to child peers or store control, and tracks child init completion before marking admin flush.

## State And Persistence Behavior
Split creates temporary child tablets under `SPLIT_PREFIX` and a derived tablet at `tablet_path(parent_id, split_log_index)`. Apply-side region state gets the derived region and tablet index but peer-side `state_changes_mut().put_region_state` and dirty mark persistence complete the durable metadata update. Dirty tablets are trimmed asynchronously; `on_tablet_trimmed` clears dirty marks and storage dirty-data state. Child peers initialize from synthetic snapshots with raft init index/term.

## Dependencies And Integration Points
Depends on split-check scheduler, PD split id/reporting paths, tablet checkpointers, raft snapshot metadata, `StoreMeta` readers, shared read tablets, transaction lock splitting, tablet trim worker, router/store control messages, `ApplyMetrics`, and admin validation from raftstore.

## Risks And Edge Cases
Splitting dirty tablets is rejected to avoid repeated trim compaction work. The first append message for a new split peer may be held while parent split initialization races. Shutdown during callback routing is tolerated. Derived-left versus derived-right changes peer id assignment and region boundaries. Approximate size/key sharing is heuristic. Crash/restart safety relies on atomic checkpoints and persisted dirty marks.

## Test Signals
`test_split` exercises invalid peer id counts, empty split requests, out-of-range and empty keys, non-ascending keys, right/left derive layouts, multi-split epoch updates, child peer ids, checkpoint paths, and forced flush of pending writes before split. Runtime signals include split metrics, PD batch split reports, split trace completion, dirty mark writes, and failpoints.
