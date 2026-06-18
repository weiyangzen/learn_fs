# sources/test-tools/xfstests/tests/generic/382

## Purpose
When default quota is set, all different quota types inherits the same default value, include group quota. So if a user quota limit larger than the default user quota value, it will still be limited by the group default quota value. There's a patch from Upstream can fix this bug: [PATCH] xfs: Split default quota limits by quota type V4. It is registered as generic/382 with `_begin_fstest` tags `auto, quick, quota`, making it part of the quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: do_test. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: quota accounting. Key helper behavior includes: formats a fresh scratch filesystem; unmounts the scratch filesystem; forces filesystem writeback/transaction commit.

## Control Flow
formats the scratch filesystem; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; wraps repeated scenarios in local helper functions do_test.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_scratch; _require_quota; _require_xfs_quota_foreign; _require_user; _require_group.

External/helper commands: $XFS_IO_PROG, grep, rm.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: === user quota test ===; user blocks and inode limit; fsgqa 0 40960 40960 00 [--------] 0 40 40 00 [--------]; wrote 31457280/31457280 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); === group quota test ===. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
