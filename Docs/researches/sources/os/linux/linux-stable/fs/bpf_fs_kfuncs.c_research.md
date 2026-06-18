# File Research: sources/os/linux/linux-stable/fs/bpf_fs_kfuncs.c

## Summary
Exports filesystem-related BPF kfuncs for BPF LSM programs: file reference management, path formatting, restricted xattr reads/writes, and cgroupfs xattr reads.

## Main Responsibilities
- Provides `bpf_get_task_exe_file()` / `bpf_put_file()` with verifier acquire/release metadata.
- Provides `bpf_path_d_path()` as a safer pathname resolver.
- Allows BPF LSM reads of `user.*` and `security.bpf.*` xattrs.
- Allows BPF LSM writes/removals only for `security.bpf.*` xattrs.
- Handles locked and unlocked dentry xattr variants.
- Registers BTF kfunc IDs and filters them to BPF LSM programs.

## Important Behavior
Dynptr xattr buffers are validated through kernel dynptr helpers before VFS xattr calls. Write helpers use `inode_permission()` and `__vfs_setxattr()` / `__vfs_removexattr()`, notify fsnotify on success, and intentionally skip LSM post hooks to avoid recursive BPF LSM deadlocks.

`bpf_lsm_has_d_inode_locked()` checks the attach target against a BTF set of LSM hooks whose inode is already locked, allowing callers to choose locked xattr variants.

## Risks
The xattr namespace restrictions are the main security boundary. Calling the unlocked variant from an already-locked LSM hook would deadlock; calling the locked variant without the lock would violate VFS locking expectations. Acquire/release annotations for file refs must remain correct for verifier enforcement.
