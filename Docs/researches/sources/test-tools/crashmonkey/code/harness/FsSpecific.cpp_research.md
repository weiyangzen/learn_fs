# sources/test-tools/crashmonkey/code/harness/FsSpecific.cpp

Purpose: implements filesystem-specific command generation, post-replay mount options, fsck return-code interpretation, UUID regeneration commands, and post-workload writeback delays.

Important APIs/functions: `GetFsSpecific()` returns a subclass for `ext2`, `ext3`, `ext4`, `btrfs`, `f2fs`, or `xfs`. `ExtFsSpecific` builds `mkfs`, mount options, `fsck`, `tune2fs`, and parses ext fsck bitmasks. `BtrfsFsSpecific`, `F2fsFsSpecific`, and `XfsFsSpecific` build their respective check/UUID commands and map coarse return codes into `FileSystemTestResult`.

Control flow: `Tester::set_fs_type()` creates an implementation based on CLI `--fs-type`. Formatting, post-replay mount, fsck, snapshot UUID changes, and post-run delay all dispatch through the polymorphic interface.

State and persistence behavior: `ExtFsSpecific` stores fs type and delay. Commands mutate disks by formatting, repairing/checking, and changing UUIDs. The post-replay mount options can trigger kernel recovery/orphan cleanup before fsck runs.

Dependencies: external tools include `mkfs`, `fsck`, `tune2fs`, `btrfs check`, `btrfstune`, `xfs_repair`, `xfs_admin`, and `fsck.f2fs`. Build macros such as `TWO_SEC`, `THREE_THIRTEEN`, `FOUR_FOUR`, `FOUR_FIFTEEN`, and `FOUR_SIXTEEN` tune delays.

Risks: command strings are shell-concatenated without escaping device paths. `ExtFsSpecific::GetFsTypeString()` always returns `ext4` even for ext2/ext3 objects. Btrfs maps return code `0` to `kFixed` rather than `kClean`, which affects result classification. F2fs and Xfs return-code interpretation is deliberately approximate. `yes | btrfs check` and repair-style tools may change the device, making results dependent on checker behavior.

Test signals: the main signals are harness phase success/failure for mkfs, mount, fsck/checker return classification, and timing delays sufficient to capture writeback on target kernels.
