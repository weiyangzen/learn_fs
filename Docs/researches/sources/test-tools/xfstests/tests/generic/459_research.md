# sources/test-tools/xfstests/tests/generic/459

## Purpose
Test buffer filesystem error recovery during a full overcommited dm-thin device. When a dm-thin device reaches its full capacity, but the virtual device still shows available space, the filesystem should be able to handle such cases failing its operation without locking up. This test has been created first to cover a XFS problem where it loops indefinitely in xfsaild due items still in AIL. The buffers containing such items couldn't be resubmitted because the items were flush locked. But, once this doesn't require any special filesystem feature to be executed, this has been integrated as a generic test. This test might hang the filesystem when ran on an unpatched kernel. It is registered as generic/459 with `_begin_fstest` tags `auto, freeze, thin`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, is_shutdown_or_ro. Important state variables and paths include lvmsuffix=${seq}_$(hostname -s | tr '-' '_')_$$, vgname=vg_$lvmsuffix, lvname=lv_$lvmsuffix, poolname=pool_$lvmsuffix, snapname=snap_$lvmsuffix, origpsize=200, virtsize=300, newpsize=300, freezeid=$!, ret=$?. Topic focus: preallocation/range operations. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem.

## Control Flow
formats the scratch filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup, is_shutdown_or_ro.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_scratch_nolvm; _require_dm_target thin-pool; _require_dm_target snapshot; _require_command $LVM_PROG lvm; _require_command "$THIN_CHECK_PROG" thin_check; _require_freeze; _require_odirect.

External/helper commands: $XFS_IO_PROG, grep, mount, rm, touch.

Representative `xfs_io` operations: pwrite -b 1m 0 220m.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Test OK. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
