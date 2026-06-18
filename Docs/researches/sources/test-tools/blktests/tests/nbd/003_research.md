<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/003 -->
# sources/test-tools/blktests/tests/nbd/003

Purpose: Network Block Device coverage that exercises module loading, exported file-backed devices, partition handling, resize, disconnect, mount, and concurrent socket clearing. This specific test is declared as: "mount/unmount concurrently with NBD_CLEAR_SOCK".

Important APIs/types/functions: sourced libraries `tests/nbd/rc`; top-level variables `DESCRIPTION=mount/unmount concurrently with NBD_CLEAR_SOCK`, `QUICK=1`; functions `requires()` lines 13-16, `test()` lines 18-31; external commands `echo`, `nbd-client`, `mkfs.ext4`, `umount`.

Control flow: `requires()` uses gates `_have_nbd`, `_have_src_program mount_clear_sock`. `test()` uses commands `echo`, `nbd-client`, `mkfs.ext4`, `umount`.

State and persistence behavior: touches state paths such as `/dev/nbd0`, `/dev/null`, `$FULL` creates filesystems or mountpoints and must unwind them during cleanup writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nbd` suite and the shared harness; through `tests/nbd/rc`; requirement gates include `_have_nbd`, `_have_src_program mount_clear_sock`; runtime command surface includes `echo`, `nbd-client`, `mkfs.ext4`, `umount`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/003 -->
