# sources/test-tools/xfstests/tests/generic/411

## Purpose
This test cover linux commit 7ae8fd0, kernel two mnt_group_id == 0 (no peer)vfsmount as peers. It case kernel dereference a NULL address. It is registered as generic/411 with `_begin_fstest` tags `auto, quick, mount`, making it part of the ACL/permission semantics, fiemap/bmap reporting, rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, fs_stress, find_mnt, start_test, end_test, crash_test. Important state variables and paths include MNTHEAD=$TEST_DIR/$seq, mpA=$MNTHEAD/"$$"_mpA, mpB=$MNTHEAD/"$$"_mpB, mpC=$MNTHEAD/"$$"_mpC. Topic focus: ACL/permission semantics, fiemap/bmap reporting, rename/link persistence. Key helper behavior includes: formats a fresh scratch filesystem; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, fs_stress, find_mnt, start_test, end_test, crash_test.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_scratch; _require_local_device $SCRATCH_DEV.

External/helper commands: $MOUNT_PROG, chown, mkdir, mount, rm, rmdir, sed, sort.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment; depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: ------; TEST_DIR/411 SCRATCH_DEV; mpA SCRATCH_DEV; mpA/mnt1 SCRATCH_DEV; mpB SCRATCH_DEV; mpB/mnt1 SCRATCH_DEV. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
