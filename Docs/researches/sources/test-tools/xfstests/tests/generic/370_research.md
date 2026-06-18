# sources/test-tools/xfstests/tests/generic/370

## Purpose
Test that we are able to create and activate a swap file on a file that used to have its extents shared multiple times. It is registered as generic/370 with `_begin_fstest` tags `auto, quick, clone, swap`, making it part of the swapfile activation, reflink/shared extents, ACL/permission semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, run_test. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: swapfile activation, reflink/shared extents, ACL/permission semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem; forces filesystem writeback/transaction commit; requires reflink support on scratch; creates a swapfile with valid swap layout; activates a swapfile through the helper.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; exercises clone/dedupe shared-extent operations; forces durability boundaries with sync/fsync operations; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, run_test.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers; persists extended-attribute namespace/value state; observes inode mode, ownership, ACL, and permission state; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/preamble, common/reflink.

Prerequisite gates: _require_scratch_swapfile; _require_scratch_reflink; _require_cp_reflink.

Documented regression fixes: _fixed_by_fs_commit btrfs 03018e5d8508 "btrfs: fix swap file activation failure due to extents that used to be shared"; _fixed_by_fs_commit xfs 2d873efd174b "xfs: flush inodegc before swapon".

External/helper commands: $ATTR_PROG, $CHATTR_PROG, chmod, rm, swapoff, swapon, sync, touch.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment; depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: Test without sync after creating and removing clones; Creating swap file...; Cloning swap file...; Deleting original file and all clones except the last...; Activating swap file...; Test with sync after creating clones. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
