<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/433 -->
# sources/test-tools/xfstests/tests/xfs/433

## Purpose
Regression test for an XFS NULL xattr buffer problem during unlink. XFS had a bug where the attr fork walk during file removal could go off the rails due to a stale reference to content of a released buffer. Memory pressure could cause this reference to point to free or reused memory and cause subsequent attribute fork lookups to fail, return a NULL buffer and possibly crash. This test emulates this behavior using an error injection knob to explicitly disable buffer LRU caching. This forces the attr walk to execute under conditions where each buffer is immediately freed on release. Commit f35c5e10c6ed ("xfs: reinit btree pointer on attr tree inactivation walk") fixed the bug. In this subset it exercises extended attribute metadata behavior. The script is an xfstests shell test, so its externally visible contract is the combination of `_begin_fstest` group tags, requirement gates, generated workload, and golden output or explicit failure conditions.

## Important APIs, Types, And Functions
The test declares `_begin_fstest auto quick attr`. It imports common/preamble, common/attr, common/inject. Local helpers are no local shell helpers. Requirement and fix gates include `_require_xfs_io_error_injection buf_lru_ref`; `_require_scratch`; `_require_attrs`. External tools and command surfaces visible in the source include `xfs_io`, `setfattr`, `mount`, `stat`, `sed`, `file`, `touch`, `rm`. Key shell state is carried in `file`, together with xfstests globals such as `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$TEST_DIR`, `$tmp`, and `$seqres.full`.

## Control Flow
The script first loads `common/preamble`, registers the test groups, imports helper libraries, and checks the feature gates. The source-derived execution path includes line 29: `_require_xfs_io_error_injection buf_lru_ref`; line 33: `_scratch_mkfs > $seqres.full 2>&1`; line 34: `_scratch_mount`; line 39: `touch $file`; line 40: `for i in $(seq 0 499); do`; line 41: `$SETFATTR_PROG -n trusted.user.$i -v 0 $file`; line 45: `_scratch_cycle_mount || _fail "cycle mount failure"`; line 48: `_scratch_inject_error buf_lru_ref 1`; line 49: `rm -f $file`; plus 2 further source-derived command steps.. error injection knobs: buf_lru_ref The final path sets `status=0` only after those checks finish, which makes unexpected command output or nonzero status part of the regression signal.

## State And Persistence Behavior
State is primarily filesystem state on the scratch or test mount plus temporary files under `$tmp.*`, `$TEST_DIR`, and `$seqres.full`. The test may create files, directories, reflinks, quota records, xattrs, metadump images, damaged metadata, or device-mapper/scsi-debug devices depending on its groups. Cleanup handlers remove temporary artifacts and unmount scratch media; tests that deliberately corrupt metadata use `_require_scratch_nocheck`, explicit unmount/remount, repair, scrub, or module reload paths to avoid treating the corruption as ordinary persistent state.

## Dependencies And Integration Points
This file integrates the xfstests harness with XFS userspace tools and kernel features. The important dependencies are the imported common helpers, feature probes such as `_require_scratch`, `_require_xfs_io_command`, `_require_xfs_scratch_rmapbt`, `_require_scratch_reflink`, quota/realtime/fuzzy gates when present, and the specific XFS tools invoked by the command flow. It also depends on the `.out` golden file and xfstests filtering conventions for stable output.

## Risks And Test Signals
Risks include error-injection timing and shutdown/recovery behavior are kernel-sensitive. Successful execution is reported through `status=0`, silence/golden stdout where expected, and any explicit `_fail`, diff, grep-count, quota-report, repair, scrub, mount, or dmesg mismatch becoming a test failure.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/433 -->
