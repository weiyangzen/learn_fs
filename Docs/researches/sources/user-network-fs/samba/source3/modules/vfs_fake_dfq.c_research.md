# sources/user-network-fs/samba/source3/modules/vfs_fake_dfq.c

## Purpose
`vfs_fake_dfq.c` fakes disk-free, quota, and selected stat values from smb.conf parameters for tests.

## Important APIs, Types, And Functions
`dfq_load_param()` reads `fake_dfq:<section>/<param>/<path>`. `dfq_disk_free()` fakes block size, free blocks, and disk size. `dfq_get_quota()` fakes quota fields for user, group, and default quota sections, including injected `err` and `nosys`. `dfq_fake_stat()` can set fake setgid group from `stat/sgid`.

## Control Flow
Disk-free and quota resolve real paths first. If no fake block size is configured, they delegate. Otherwise they fill caller outputs from config. Stat wrappers delegate and then overlay setgid group when configured.

## State And Persistence
No private state exists. All fake values live in Samba configuration; the filesystem is not modified.

## Dependencies And Integration Points
The module depends on VFS realpath, disk-free, quota, stat hooks, full-path helpers, loadparm parametric options, and `SMB_DISK_QUOTA`.

## Risks
Path-keyed config is brittle across realpath changes. Disk-free math can be odd for block sizes below 1024 that do not divide 1024. Zero block size means delegate, so zero cannot be returned. gid zero cannot be faked by `stat/sgid`.

## Test Signals
Test fake disk-free math, delegation when absent, every quota type and field, ENOTSUP/ENOSYS injection, stat/fstat/lstat/fstatat setgid overlays, and realpath-dependent keying.
