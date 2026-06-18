<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_region_heartbeat.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_region_heartbeat.rs

## Purpose
This file tests raftstore region heartbeat reporting to PD: down peers, pending peers, heartbeat timestamps, heartbeat terms, and approximate-size behavior across leader changes.

## Important APIs, Types, and Functions
The `test_down_peers!` macro drives down-peer detection. `test_pending_peers` drives snapshot-blocked peer addition. Test functions include hibernate/non-hibernate down-peer variants, node/server pending-peer variants, `test_region_heartbeat_timestamp`, `test_region_heartbeat_term`, and `test_region_heartbeat_leader_change`.

It uses `ReadableDuration`, `ReadableSize`, `DropSnapshotFilter`, PD heartbeat inspection methods such as `get_down_peers`, `get_pending_peers`, `get_region_last_report_ts`, `get_region_last_report_term`, and approximate-size getters.

## Control Flow and Behavior
Down-peer tests stop nodes, wait for PD to report them down, restart nodes, transfer leadership, and verify stale down-peer seconds are reset instead of reused. Pending-peer tests block snapshots to a new peer, require PD to report the peer pending, then unblock and require pending state to disappear.

Timestamp and term tests transfer leaders and poll PD metadata until report timestamp or term advances. The leader-change stats test forces split-check/heartbeat behavior, grows approximate region size, transfers leadership, grows again, adds peers to trigger heartbeats, and confirms approximate size is not reset to stale lower values after transferring back.

## State and Persistence
The file observes PD-side heartbeat state rather than local disk directly: down-peer maps, pending-peer maps, last report timestamp, last report term, and approximate size. It also relies on raftstore local apply/snapshot progress to clear pending peers.

## Dependencies and Integration Points
The tests integrate cluster node lifecycle, hibernate-region configuration, PD client state, snapshot transport filters, split-check ticks, leader transfer, and heartbeat tick intervals.

## Risks
Heartbeat tests are timing-heavy. Regressions include hibernated regions delaying down-peer reports unexpectedly, stale down-peer seconds surviving leader transfer, pending peers not clearing after snapshot delivery, heartbeat term/timestamp not advancing, and approximate stats regressing after leadership changes.

## Test Signals
Signals are PD map contents, increasing timestamp/term values, eventual approximate size thresholds, exact pending peer identity, and successful data writes that force heartbeat state refresh.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_region_heartbeat.rs -->
