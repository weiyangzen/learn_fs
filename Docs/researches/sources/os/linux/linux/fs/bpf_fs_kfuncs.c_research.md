# File Research: sources/os/linux/linux/fs/bpf_fs_kfuncs.c

Purpose: Exposes selected filesystem operations as BPF kfuncs, primarily for BPF LSM programs.

Provided kfuncs:
- `bpf_get_task_exe_file()`: acquires a referenced `struct file *` for a task’s executable file.
- `bpf_put_file()`: releases file references acquired by BPF.
- `bpf_path_d_path()`: safer path-to-string resolver built on `d_path()`.
- `bpf_get_dentry_xattr()` and `bpf_get_file_xattr()`: read allowed xattrs into BPF dynptr buffers.
- `bpf_set_dentry_xattr()` and `bpf_remove_dentry_xattr()`: set/remove allowed BPF security xattrs with inode locking.
- `bpf_cgroup_read_xattr()`: when cgroups are enabled, reads `user.*` xattrs from cgroupfs kernfs nodes.
- `bpf_real_inode()`: resolves a dentry to its real backing inode for overlay/union filesystems.

Permission model:
- Xattr reads are limited to `user.*` and `security.bpf.*`, then checked with `inode_permission(..., MAY_READ)`.
- Xattr writes/removes are limited to `security.bpf.*`, then checked with `inode_permission(..., MAY_WRITE)`.
- Cgroup xattr reads are limited to `user.*`.

Locking and LSM integration:
- Locked helpers `bpf_set_dentry_xattr_locked()` and `bpf_remove_dentry_xattr_locked()` are provided for LSM hooks that already hold `d_inode`.
- Unlocked kfuncs take and release `inode_lock()`.
- Post-xattr security hooks are deliberately not called for BPF LSM-originated xattr changes to avoid recursive deadlocks.
- `d_inode_locked_hooks` lists BPF LSM hooks where the inode is already locked.

BTF registration:
- `BTF_KFUNCS_START(bpf_fs_kfunc_set_ids)` publishes kfuncs with flags such as `KF_ACQUIRE`, `KF_RELEASE`, `KF_RET_NULL`, and `KF_SLEEPABLE`.
- `bpf_fs_kfuncs_filter()` allows these kfuncs for BPF LSM programs and rejects other program types.
- Registration happens at `late_initcall`.

Risk notes: The security boundary is the xattr prefix filtering plus inode permissions. Dynptr size/data validation and correct locked-vs-unlocked helper selection are central to avoiding verifier, memory, and deadlock problems.
