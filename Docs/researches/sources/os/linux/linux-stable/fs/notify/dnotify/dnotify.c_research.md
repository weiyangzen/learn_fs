# File Research: sources/os/linux/linux-stable/fs/notify/dnotify/dnotify.c

Purpose: Legacy directory notification implementation built on fsnotify. It supports `fcntl()`-based dnotify watches on directories and delivers events via `SIGIO`/poll notifications.

Core structures and globals:
- `dir_notify_enable` controls whether dnotify registration is accepted; when sysctl is enabled it is exposed as `fs/dir-notify-enable`.
- `dnotify_struct_cache` and `dnotify_mark_cache` are slab caches for per-watch and per-inode-mark state.
- `dnotify_group` is the single fsnotify group for dnotify.
- `struct dnotify_mark` wraps an `fsnotify_mark` plus a linked list of `struct dnotify_struct` entries for all file descriptors watching the inode.

Important behavior:
- `dnotify_recalc_inode_mask()` recalculates the aggregate inode event mask from all attached dnotify watch entries and updates fsnotify core masks.
- `dnotify_handle_event()` receives fsnotify inode events, filters non-directory cases, sends `SIGIO` to interested watchers, and removes one-shot watchers that lack `FS_DN_MULTISHOT`.
- `dnotify_flush()` removes the watch entry for a file descriptor on close and detaches/frees the fsnotify mark when the last watcher is gone.
- `convert_arg()` maps userspace `DN_*` flags to fsnotify `FS_*` masks, always including `FS_EVENT_ON_CHILD`.
- `attach_dn()` either appends a new watcher to the mark list or ORs a new mask into an existing watcher for the same owner/file.
- `fcntl_dirnotify()` is the registration entry point: it validates enablement, directory-ness, security policy, allocates state, handles fd-close races with `fget_raw()`, sets file ownership for signals, attaches the watcher, and handles cleanup paths.
- `dnotify_init()` creates caches, allocates the fsnotify group, and registers the sysctl.

Dependencies and interfaces:
- Externally callable functions include `dnotify_flush()` and `fcntl_dirnotify()`.
- Uses fsnotify backend mark/group APIs, Linux security hook `security_path_notify()`, and signal ownership helpers.

Concurrency and lifetime:
- Uses the fsnotify group lock and per-mark spinlock to coordinate mark list updates.
- Handles the race where a file descriptor is closed during registration by comparing `fget_raw(fd)` result against `filp`.
- One-shot watchers are freed during event delivery while holding the mark lock.

Design notes and risks:
- dnotify is compatibility code; Kconfig help explicitly points users toward superior alternatives.
- Watcher lifetime is tied to file descriptor ownership and close handling, so mistakes in ownership or flush paths can leak or prematurely remove notifications.
- The implementation relies on linked-list mutation under spinlock; changes should be made cautiously.
