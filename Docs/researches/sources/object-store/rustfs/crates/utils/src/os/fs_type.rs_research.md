# sources/object-store/rustfs/crates/utils/src/os/fs_type.rs

## Purpose
Maps Linux filesystem magic numbers from `statfs` into human-readable filesystem type strings for disk diagnostics.

## Important APIs, Types, And Functions
`get_fs_type(fs_type: u64) -> &'static str` is crate-private and returns names for TMPFS, MSDOS, NFS, EXT4, ecryptfs, overlayfs, REISERFS, XFS, BTRFS, CEPH, EXFAT, EROFS, F2FS, ISOFS, FUSE, SQUASHFS, CIFS, SMB2, V9FS, and BCACHEFS, with `UNKNOWN` fallback. Comments list unverified magic values deliberately left out.

## Control Flow And State
Pure match expression, no state or IO.

## Dependencies And Integration Points
Compiled on Linux and in tests through `os/mod.rs`; `linux.rs::get_info` uses it to populate `DiskInfo.fstype`.

## Risks And Test Signals
The mapping can drift as new filesystems appear or magic constants differ. Unknown values remain safe but less informative. Tests verify representative common and verified Linux UAPI magic numbers.
