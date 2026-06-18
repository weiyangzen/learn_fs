# File Research: sources/os/linux/linux-stable/fs/proc/namespaces.c

Implements `/proc/<pid>/ns` directory and namespace symlinks.

Key points:
- Builds `ns_entries[]` from enabled namespace types: net, uts, ipc, pid, pid_for_children, user, mount, cgroup, time, and time_for_children.
- Namespace symlink readlink/get_link require `ptrace_may_access(..., PTRACE_MODE_READ_FSCREDS)`.
- `proc_ns_get_link()` resolves to an nsfs path using `ns_get_path()` and `nd_jump_link()`.
- `proc_ns_readlink()` formats namespace names with `ns_get_name()`.
- Lookup and readdir instantiate symlink inodes with `proc_pid_make_inode()`, store `ns_ops`, and use PID dentry operations.
- Directory inode ops use PID getattr and forbid chmod via `proc_nochmod_setattr`.

Dependencies/contracts:
- Security depends on ptrace access checks.
- Bridges procfs PID entries with nsfs namespace file identity.
