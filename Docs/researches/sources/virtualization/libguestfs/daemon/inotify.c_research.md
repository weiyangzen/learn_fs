# File Research: sources/virtualization/libguestfs/daemon/inotify.c

Implements optional inotify watch/read APIs.

Important behavior:
- Optional under `HAVE_SYS_INOTIFY_H`.
- Maintains a global nonblocking close-on-exec inotify fd and a 64 MiB static event buffer.
- `do_inotify_init` requires a mounted root and may write `/proc/sys/fs/inotify/max_queued_events`.
- `do_inotify_add_watch` watches `sysroot_path(path)`.
- `do_inotify_read` drains available events, preserves incomplete events in `inotify_buf`, and estimates protocol message space.
- `do_inotify_files` reads all pending events, sorts unique non-empty names through `sort -u`, and returns them.

Filesystem relevance: exposes Linux filesystem event monitoring for guest-root paths during daemon sessions.
