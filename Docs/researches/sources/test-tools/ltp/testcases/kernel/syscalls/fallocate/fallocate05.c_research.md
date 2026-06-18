# sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate05.c

Purpose: Tests that writes to preallocated space continue to work after the filesystem is filled, then verifies hole punching frees space.

Important APIs/types/functions: `fallocate`, `write`, `tst_fill_fs`, `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE`, `lseek(SEEK_HOLE/SEEK_DATA)`, and filesystem-type checks for btrfs/bcachefs.

Control flow: The test preallocates 256 blocks, fills the filesystem, writes into preallocated space, keeps allocating one block at a time until `ENOSPC`, writes into any extra allocated space, punches a hole, writes again, and checks hole/data offsets.

State and persistence behavior: State is a deliberately full mounted filesystem and a large preallocated test file. Hole size expectations vary for extent-oriented filesystems.

Dependencies and integration points: Requires root, mounted device, all-filesystems mode, and a generous timeout.

Risks and test signals: Disk-full tests are inherently filesystem-sensitive. Expected signals are successful writes to reserved blocks, `ENOSPC` for new allocation, and correct hole reporting.
