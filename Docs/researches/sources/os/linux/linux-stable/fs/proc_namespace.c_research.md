# File Research: sources/os/linux/linux-stable/fs/proc_namespace.c

## Summary
Implements `/proc/<pid>/mounts`, `/proc/<pid>/mountinfo`, and `/proc/<pid>/mountstats`. It opens a target task's mount namespace and root, then renders namespace mount entries using seq_file helpers.

## Main Responsibilities
- Format legacy mount table lines, mountinfo lines, and mount statistics lines.
- Escape mount paths, filesystem names, device names, and option strings for proc output.
- Show superblock options, VFS mount options, idmapped status, propagation tags, and filesystem-specific options/statistics.
- Track mount namespace events for polling on mounts and mountinfo.
- Hold references to the target task's mount namespace and root path while the proc file is open.

## Key Interfaces
- `proc_mounts_operations`, `proc_mountinfo_operations`, and `proc_mountstats_operations` export file operations.
- `show_vfsmnt()` renders `/proc/<pid>/mounts`.
- `show_mountinfo()` renders `/proc/<pid>/mountinfo`.
- `show_vfsstat()` renders `/proc/<pid>/mountstats`.
- `mounts_open_common()` captures the task, mount namespace, and root path shared by all three files.
- `mounts_poll()` reports namespace event changes via `EPOLLERR | EPOLLPRI`.

## Important Behavior
The output is relative to the target task's root. Mountpoints outside that root can cause `seq_path_root()` to return `SEQ_SKIP`, hiding entries from the chrooted view. Mountinfo additionally reports shared/slave/unbindable propagation tags and `propagate_from` when the visible root changes propagation ancestry.

## State and Synchronization
Each open seq_file owns a `struct proc_mounts` with a mount namespace reference, root path reference, and selected show callback. `mounts_release()` drops both references.

## Cross-File Interactions
The file is procfs-adjacent but lives under `fs/` because it relies on namespace internals from `fs/namespace.c`, `pnode.h`, and VFS mount structures.

## Risks
Output correctness depends on escaping fields exactly as proc consumers expect. Polling relies on namespace event counters, so callers should treat `EPOLLPRI` as a signal to reread rather than as a precise change descriptor.
