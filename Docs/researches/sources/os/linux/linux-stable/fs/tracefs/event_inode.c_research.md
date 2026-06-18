# File Research: sources/os/linux/linux-stable/fs/tracefs/event_inode.c

Purpose: Implements eventfs, the dynamic tracefs subtree that lazily materializes tracing event directories and files.

Key responsibilities:
- Defines `eventfs_inode` lifetime, reference counting, SRCU-based freeing, and mutex-protected mutation.
- Creates eventfs directory descriptors and top-level `events` directory.
- Dynamically looks up event files and subdirectories from metadata callbacks.
- Implements directory iteration without precreating all dentries/inodes.
- Caches user-modified mode/uid/gid attributes for eventfs directories and files.
- Propagates remount uid/gid changes through eventfs saved attributes.
- Removes eventfs directories recursively and invalidates the top-level events dentry.
- Exposes remount lock/unlock helpers combining mutex and SRCU.

Important interactions:
- Depends on tracefs inode allocation and dentry operations from `inode.c`.
- Uses tracing-provided `eventfs_entry` callback/release hooks.
- Uses fsnotify, security lockdown checks, RCU/SRCU, kref, and tracefs create helpers.

Notable invariants and risks:
- Callback functions run while eventfs internal locks are held and must not reenter tracefs/eventfs.
- Eventfs directory recursion is expected to stay within `events/group/event/file` depth.
- File inodes share a fixed inode number while directories get stable generated numbers.
- `is_freed` marks descriptors before SRCU and dentry references finish draining.
