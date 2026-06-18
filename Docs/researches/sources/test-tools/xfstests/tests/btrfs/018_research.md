## sources/test-tools/xfstests/tests/btrfs/018

Purpose: this quick subvolume regression test verifies that one subvolume can be moved into another subvolume.

Control flow: it requires scratch, formats and mounts it, creates `test1` and `test2` subvolumes, then runs `mv $SCRATCH_MNT/test1 $SCRATCH_MNT/test2`.

State and persistence: scratch ends with `test1` nested under `test2` if the move succeeds.

Dependencies: `_scratch_mkfs`, `_scratch_mount`, `$BTRFS_UTIL_PROG subvolume create`, and standard `mv`.

Risks: the second create failure message incorrectly says "couldn't create test1". The test checks only the move command return code, not the final subvolume topology.

Test signals: expected output is `Silence is golden`; create or move failure triggers `_fail`.
