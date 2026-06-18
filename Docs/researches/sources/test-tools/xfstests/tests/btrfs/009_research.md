## sources/test-tools/xfstests/tests/btrfs/009

Purpose: this quick subvolume regression test verifies that deleting the current default subvolume does not make the filesystem unmountable.

Control flow: it formats and mounts scratch, creates subvolume `newvol`, obtains its subvolume id, sets it as default, attempts to delete the subvolume, unmounts, and then requires that mounting scratch still succeeds.

State and persistence: scratch default subvolume metadata is changed. The delete command output is logged but not asserted directly; the final mount is the behavioral check.

Dependencies: `_require_scratch`, `_scratch_mkfs`, `_scratch_mount`, `_scratch_unmount`, `_try_scratch_mount`, `$BTRFS_UTIL_PROG`, and `_btrfs_get_subvolid`.

Risks: if deletion behavior changes to a different error message but mount still works, the test still passes. A successful delete followed by mount success would be surprising but not separately checked beyond btrfs semantics and golden output.

Test signals: expected stdout is `Silence is golden`. Failure occurs if create/set-default fail or the post-delete mount fails.
