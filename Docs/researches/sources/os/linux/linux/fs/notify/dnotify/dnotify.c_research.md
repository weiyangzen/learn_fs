# File Research: sources/os/linux/linux/fs/notify/dnotify/dnotify.c

Purpose: Legacy directory notification implementation built on fsnotify. It supports `fcntl()`-based directory watches tied to file descriptors and delivers events through `SIGIO`/poll notifications.

Core structures and globals:
- `dir_notify_enable` gates dnotify registration and may be exposed as `fs/dir-notify-enable` under sysctl.
- `dnotify_struct_cache` and `dnotify_mark_cache` allocate watcher and mark state.
- `dnotify_group` is the single fsnotify group used by dnotify.
- `struct dnotify_mark` wraps an `fsnotify_mark` plus a linked list of `struct dnotify_struct` watchers.

Important behavior:
- `dnotify_recalc_inode_mask()` recomputes aggregate inode interest from all linked dnotify watchers.
- `dnotify_handle_event()` filters non-directory cases, sends `SIGIO` to matching watchers, and removes one-shot watchers lacking `FS_DN_MULTISHOT`.
- `dnotify_flush()` removes a file descriptor’s watch on close and detaches/frees the mark when no watchers remain.
- `convert_arg()` translates userspace `DN_*` flags into fsnotify `FS_*` masks and always includes `FS_EVENT_ON_CHILD`.
- `attach_dn()` either appends a new watcher or ORs a new mask into an existing watcher for the same owner/file.
- `fcntl_dirnotify()` validates enablement, directory-ness, security policy, allocation, fd-close races, signal ownership, and mark attachment.
- `dnotify_init()` creates slab caches, allocates the fsnotify group, and registers sysctl state.

Dependencies and interfaces:
- Externally used functions include `dnotify_flush()` and `fcntl_dirnotify()`.
- Uses fsnotify mark/group APIs, `security_path_notify()`, file ownership helpers, and signal delivery helpers.

Concurrency and lifetime:
- Uses the fsnotify group lock and per-mark spinlock for watcher list mutation.
- Handles fcntl/close races by comparing `fget_raw(fd)` with the original `filp`.
- One-shot watchers are freed during event delivery under the mark lock.

Design notes and risks:
- Compatibility code with lifetime tied to file descriptor ownership.
- Linked-list mutation under spinlock and mark detach/free sequencing are the main correctness-sensitive paths.
