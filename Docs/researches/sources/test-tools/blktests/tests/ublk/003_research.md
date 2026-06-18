<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/003 -->
# sources/test-tools/blktests/tests/ublk/003

Purpose: ublk userspace block-driver coverage for add/delete, mount, crash, recovery, and daemon-kill behavior. This specific test is declared as: "test mounting block device exported by ublk".

Important APIs/types/functions: sourced libraries `tests/ublk/rc`; top-level variables `DESCRIPTION=test mounting block device exported by ublk`; functions `requires()` lines 11-13, `test()` lines 15-50; external commands `ublk`, `mkfs.ext4`, `echo`, `mount`, `umount`.

Control flow: `requires()` uses commands `mkfs.ext4`; gates `_have_program mkfs.ext4`. `test()` uses commands `echo`, `mount`, `umount`.

State and persistence behavior: touches state paths such as `/dev/ublkb0`, `/dev/null`, `$TMPDIR/mnt`, `$TMPDIR/img`, `$FULL`, `$(findmnt -l -o FSTYPE -n "$mnt")` creates filesystems or mountpoints and must unwind them during cleanup writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `ublk` suite and the shared harness; through `tests/ublk/rc`; requirement gates include `_have_program mkfs.ext4`; runtime command surface includes `ublk`, `mkfs.ext4`, `echo`, `mount`, `umount`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/003 -->
