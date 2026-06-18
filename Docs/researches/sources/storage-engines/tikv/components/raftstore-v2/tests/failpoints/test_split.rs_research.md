# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_split.rs

## Purpose
This failpoint test verifies split recovery when metadata is persisted before the new tablet is physically installed. It ensures restart resumes tablet installation and both resulting regions can serve writes with the correct epoch.

## Important APIs, Types, and Functions
- `test_restart_resume()` uses failpoint `async_write_before_cb` to stop async metadata write before callback completion.
- It uses `split_region()` to create region 1000 from region 2, then submits a write to force split initialization.
- It reads raft-engine `RegionLocalState.tablet_index` and the expected tablet path from `TabletRegistry`.

## Control Flow
The test activates the failpoint, splits region 2, submits a write to region 2 to ensure split init begins, and verifies raft metadata for region 1000 exists while its tablet path does not. After restart, the path must exist. The failpoint is then removed because replaying the split would otherwise block writes. The test loops until region epochs match, then writes to both resulting regions.

## State and Persistence Behavior
It validates durable raft-engine split metadata and deferred tablet-directory creation. It also checks replay after restart installs the missing tablet and updates source-region epoch.

## Dependencies and Integration Points
It uses split helper admin commands, raft-engine state APIs, tablet registry path conventions, router request construction, and simple write routing.

## Risks and Edge Cases
- Persisted split metadata without a tablet directory must be recoverable.
- Source peer replay may lag after restart, so tests wait for epoch convergence.
- Leaving the failpoint enabled would deadlock replay writes, which the test explicitly avoids.

## Test Signals
Assertions cover initial `RAFT_INIT_LOG_INDEX`, missing tablet path before restart, existing path after restart, matching region epoch, and successful writes to both regions.
