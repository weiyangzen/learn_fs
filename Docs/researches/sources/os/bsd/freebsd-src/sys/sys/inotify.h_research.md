# File Research: sources/os/bsd/freebsd-src/sys/sys/inotify.h

Defines FreeBSD’s Linux-compatible inotify ABI and kernel vnode event hooks. User-visible pieces include `struct inotify_event`, `inotify_init`, `inotify_init1`, `inotify_add_watch`, `inotify_add_watch_at`, and `inotify_rm_watch`.

Event and flag masks mirror Linux-style inotify semantics: access, modify, attrib, close, open, move, create, delete, delete-self, move-self, one-shot, mask-add/create, only-dir, no-follow, unmount, overflow, ignored, and is-dir. `_IN_NAMESIZE` computes aligned variable name storage.

Kernel macros `INOTIFY`, `INOTIFY_NAME`, `INOTIFY_MOVE`, and `INOTIFY_REVOKE` cheaply test vnode inotify flags before invoking `VOP_INOTIFY`; rename events use a shared cookie to pair moved-from and moved-to records.
