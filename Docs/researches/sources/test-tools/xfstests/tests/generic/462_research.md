# sources/test-tools/xfstests/tests/generic/462

## Purpose
This is a regression test for kernel commit ef947b2 x86, mm: fix gup_pte_range() vs DAX mappings created by Jeffrey Moyer <jmoyer@redhat.com> This is reproducible only when testing on pmem device which is configured in "memory mode", not in "raw mode". It is registered as generic/462 with `_begin_fstest` tags `auto, quick, dax, mmap`, making it part of the ACL/permission semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include md5_1=$(_md5_checksum $SCRATCH_MNT/readonlyfile), md5_2=$(_md5_checksum $SCRATCH_MNT/readonlyfile). Topic focus: ACL/permission semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_scratch_dax_mountopt "dax"; _require_test_program "t_mmap_write_ro"; _require_user.

External/helper commands: $XFS_IO_PROG, chmod, chown.

Representative `xfs_io` operations: pwrite -S 0xFF 0 4096; pwrite -S 0x00 0 4096.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: read: Bad address. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
