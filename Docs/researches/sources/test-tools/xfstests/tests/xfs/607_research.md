<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/607 -->
# sources/test-tools/xfstests/tests/xfs/607

## Purpose
`sources/test-tools/xfstests/tests/xfs/607` is an XFS fstests shell case focused on extent mapping and exchange. This is a regression test for "xfs: Fix false ENOSPC when performing direct write on a delalloc extent in cow fork". If there is a lot of free space but it is very fragmented, it's possible that a very large delalloc reservation could be created in the CoW fork by a buffered write. If a directio write tries to convert the delalloc reservation to a real extent, it's possible that the allocation will succeed but fail to convert even the first block of the directio write range. In this case, XFS will return ENOSPC even though all it needed to do was to keep converting until the allocator returns ENOSPC or the first block of the direct write got some space. The `_begin_fstest` declaration is `auto quick clone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/inject`, `./common/preamble`, `./common/reflink`. Local helper surface: `_cleanup`. Requirement and regression gates include `_fixed_by_kernel_commit d62113303d69 "xfs: Fix false ENOSPC when performing direct write on a delalloc extent in cow fork"`, `_require_test_program "punch-alternating"`, `_require_test_reflink`, `_require_xfs_io_error_injection "bmap_alloc_minlen_extent"`, `_require_test_delalloc`. Important external or harness tools detected in the full source include `xfs_io`, `punch-alternating`, `stat`. Scenario variables and harness state referenced include `TEST_DIR`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/607.out`; stable progress/output labels such as `echo "Create source file"`, `echo "Create Reflinked file"`, `echo "Set cowextsize"`, `echo "Fragment FS"`, `echo "Allocate block sized extent from now onwards"`, and 2 more; diagnostic detail appended to `$seqres.full`. The source has 84 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/607 -->
