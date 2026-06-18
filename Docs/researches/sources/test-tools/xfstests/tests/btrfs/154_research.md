# sources/test-tools/xfstests/tests/btrfs/154

## Purpose

`sources/test-tools/xfstests/tests/btrfs/154` is btrfs fstests case `154`. It targets the btrfs feature area named by its fstests tags. Source comments describe the scenario as: Test if btrfs rename handle dir item collision correctly Without patch fix, rename will fail with EOVERFLOW, and filesystem is forced readonly. This bug is going to be fixed by a patch for kernel titled "btrfs: correctly calculate item size used when item key collision happens" Currently in btrfs the node/leaf size can not be smaller than the page size (but it can be greater than the page size). So use the largest supported node/leaf size (64Kb) so that the test can run on any platform that Linux supports. In the following for loop, we'll create a leaf fully occupied by

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick` declares tags `auto quick`; environment gates are expressed through `_require*` helpers. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_command $PYTHON3_PROG python3`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs "--nodesize 65536" >>$seqres.full 2>&1`; `_scratch_mount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
