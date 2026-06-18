# File Research: sources/os/linux/linux/fs/proc/namespaces.c

## Scope

This file implements `/proc/<pid>/ns`, including namespace symlink lookup, readlink, directory iteration, and lookup.

## Public And Internal APIs Covered

- Namespace entry table: `ns_entries[]`.
- Symlink inode ops: `proc_ns_link_inode_operations`.
- Directory file ops: `proc_ns_dir_operations`.
- Directory inode ops: `proc_ns_dir_inode_operations`.

## Control Flow And Behavior

- `ns_entries[]` includes configured namespace operation tables: net, uts, ipc, pid, pid_for_children, user, mount, cgroup, time, and time_for_children.
- `proc_ns_get_link()` obtains the target task, takes `exec_update_lock`, checks ptrace read access, asks namespace code for a path, and uses `nd_jump_link()` to make the proc symlink resolve to nsfs.
- `proc_ns_readlink()` performs the same task and ptrace checks, then formats the namespace name using `ns_get_name()` and copies it to userspace.
- `proc_ns_instantiate()` creates a PID proc symlink inode, stores `ns_ops` in `PROC_I(inode)`, updates ownership, and splices with PID dentry operations.
- `proc_ns_dir_readdir()` emits `.` and `..`, then iterates configured namespace names through `proc_fill_cache()`.
- `proc_ns_dir_lookup()` matches a dentry name against `ns_entries[]` and instantiates the corresponding symlink.

## Dependencies

- Depends on proc PID inode creation, ptrace access checks, `exec_update_lock`, namespace operation tables, nsfs path/name helpers, and PID dentry operations.

## Risks And Invariants

- Namespace symlink resolution is not allowed under RCU path walk and returns `-ECHILD` when no dentry is available.
- Access is gated by `ptrace_may_access(..., PTRACE_MODE_READ_FSCREDS)`.
- The task reference is always dropped after lock and namespace operations complete.
