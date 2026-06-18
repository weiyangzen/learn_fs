# File Research: sources/virtualization/virtiofsd/src/sandbox.rs

## Purpose

This file implements virtiofsd sandbox setup. It supports namespace-based isolation, chroot-based isolation, and no isolation. The sandbox code isolates the daemon around the shared directory, captures sandbox-visible `/proc/self/fd` and `/proc/self/mountinfo` descriptors, optionally configures UID/GID maps for unprivileged user namespaces, and coordinates helper child processes.

## Main Types And Functions

- `Error`: detailed sandbox setup failures for mount, chroot, namespace, UID/GID map, group dropping, and process-control operations.
- `SandboxMode`: `Namespace`, `Chroot`, or `None`; parsed from strings.
- `Sandbox`: stores the shared directory, captured proc/mountinfo descriptors, sandbox mode, and requested UID/GID maps.
- `Sandbox::new(...)`: constructs a sandbox configuration.
- `setup_mounts()`: builds namespace mount isolation around the shared directory.
- `setup_id_mappings(uid_map, gid_map, pid)`: configures user namespace UID/GID maps for a target process.
- `enter_namespace(listener)`: creates PID/mount/network/user namespaces, configures ID mappings, forks the daemon child, and arranges parent waiting.
- `enter_chroot()`: opens proc descriptors, chroots into the shared directory, and changes to `/`.
- `must_drop_supplemental_groups()`: decides whether root must drop supplementary groups.
- `drop_supplemental_groups()`: calls `setgroups(0, NULL)` when needed.
- `enter(listener)`: validates mode and maps, drops groups if required, then enters the selected sandbox.
- Accessors: `get_proc_self_fd`, `get_mountinfo_fd`, `get_root_dir`, `get_mountinfo_prefix`.

## Namespace Mount Setup

`setup_mounts()` is the central isolation routine. It:

1. Opens `/proc/self` so `/proc/self/mountinfo` can later be opened after mount changes.
2. Marks `/` recursively slave to prevent propagation to the parent mount namespace.
3. Mounts a fresh procfs at `/proc`.
4. Bind-mounts `/proc/self/fd` over `/proc`, narrowing proc access to file descriptors.
5. Opens the bind-mounted `/proc` as the sandbox’s `proc_self_fd`.
6. Clones the shared directory tree with `open_tree(... OPEN_TREE_CLONE ...)`.
7. Moves the cloned tree to the shared directory path with `move_mount`.
8. Opens old `/`, `fchdir`s into the new root, and compares old/new root statx data.
9. If not already the current root, performs `pivot_root(".", ".")`, switches to old root, makes it slave, lazily unmounts it, and returns to the new root.
10. Opens sandbox-visible `mountinfo` via the saved `/proc/self` descriptor.

The code avoids exposing ancestor directories through `/proc/self/fd` and detaches old root state after pivoting.

## UID/GID Mapping Flow

For unprivileged namespace mode, `enter_namespace()` forks a first child whose only job is to set UID/GID mappings from outside the namespace. Synchronization uses two pipes and `IdMapSetUpPipeMessage::{Request, Done}`:

- Parent calls `unshare(flags)`.
- Parent signals the first child to write maps for the parent process.
- First child invokes `setup_id_mappings`.
- Parent waits for the done byte, then waits for the helper child.

`setup_id_mappings()` defaults to a single identity mapping for the current effective UID/GID if no maps are supplied. If requested maps require privileges or cover more than one ID, it shells out to `newuidmap` or `newgidmap`; otherwise it writes `/proc/<pid>/uid_map`, `/proc/<pid>/setgroups`, and `/proc/<pid>/gid_map` directly.

## Process Model

`enter_namespace()` uses `util::sfork()` rather than plain `fork()`, so children receive a parent-death signal and detect parent death races. After namespace setup and ID mapping, the process sets uid/gid to root inside the namespace and forks a second child. The second child runs `setup_mounts()` and continues with the vhost-user listener. The parent closes the listener FD without unlinking the socket and then calls `util::wait_for_child(child)`, which never returns.

This listener handling prevents the parent from keeping a listening socket open after the child accepts, avoiding hangs from a misconfigured VMM connecting twice.

## Chroot Mode

`enter_chroot()` is simpler:

1. Opens `/proc/self/fd` as `proc_self_fd`.
2. Opens `/proc/self/mountinfo` as `mountinfo_fd`.
3. Calls `chroot(shared_dir)`.
4. Calls `chdir("/")`.

Chroot mode is restricted to root by `enter()`.

## Validation And Security Rules

`enter()` enforces:

- Non-root cannot use `SandboxMode::Chroot`; it should use namespace mode.
- Explicit UID/GID maps are only accepted for non-root namespace mode.
- Supplementary groups are dropped when root can switch arbitrary groups, unless the process is already in a restricted user namespace with single UID/GID mappings and `setgroups` is denied.

## Integration Points

This module integrates with:

- `crate::idmap::{UidMap, GidMap, IdMapSetUpPipeMessage}` for namespace maps.
- `crate::oslib` for mount wrappers, `open_tree`, `move_mount`, `fchdir`, `umount2`, and pipes.
- `crate::passthrough::statx` to compare mount/root identity.
- `crate::util::{sfork, wait_for_child}` for safer fork/wait behavior.
- `vhost::vhost_user::Listener`, which is passed through sandbox entry.
- The broader passthrough filesystem code through `proc_self_fd`, `mountinfo_fd`, root directory, and mountinfo prefix accessors.

## Risks And Edge Cases

- Namespace setup depends on modern Linux mount APIs such as `open_tree` and `move_mount`.
- Missing `newuidmap`/`newgidmap` or invalid subordinate ID configuration causes explicit map setup failure.
- The parent exits via `wait_for_child`, so callers must expect `enter_namespace()` not to return in the parent.
- `CString::new(self.shared_dir.clone()).unwrap()` assumes the shared directory contains no interior NUL.
- `setup_mounts()` has many privileged syscalls and must stay aligned with the seccomp allowlist.
