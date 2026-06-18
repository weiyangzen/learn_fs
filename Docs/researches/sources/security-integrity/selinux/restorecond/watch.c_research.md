# sources/security-integrity/selinux/restorecond/watch.c
# sources/security-integrity/selinux/restorecond/watch.c

Purpose: implements restorecond configuration parsing, no-follow path handling, watch-list management, and the inotify event loop.

Important APIs and control flow: `safe_open()` walks path components with `O_NOFOLLOW` and `O_PATH` to avoid symlink traversal, supported by glob alternate directory functions. `watch_list_add()` expands globs, immediately calls `selinux_restorecon()` on matching existing paths, then watches the parent directory for `IN_CREATE|IN_MOVED_TO` and stores filename patterns in a per-directory list. `watch_list_find()` matches created names with `fnmatch()` and relabels matching paths. `watch()` reads inotify events, reloads config when the config file changes, routes utmp events through `utmpwatcher_handle()`, and handles normal watched-file events. `read_config()` clears existing watches, reads non-comment lines, expands `~` for current user mode or delegates to utmp watcher in root mode, and watches the config file itself.

State and persistence: owns a linked list of watched directories (`firstDir`), inotify watch descriptors, and persistent relabel side effects via `selinux_restorecon()`.

Dependencies and integration points: uses libselinux restorecon, `stringslist`, `utmpwatcher`, globals from `restorecond.h`, glob, inotify, and syslog/stderr reporting.

Risks and test signals: path safety is carefully addressed with no-follow opens and `/proc/self/fd` watching, but glob and parent-directory watching still require careful handling of races. Config reload removes and recreates all watches. No dedicated tests exercise symlink race resistance, glob behavior, or reload behavior.
