# File Research: sources/teaching/minix/minix/servers/vfs/proto.h

Global VFS prototype header. It centralizes cross-module declarations for device drivers, file descriptors, links, mount, open, path, pipe, protection, read/write, request wrappers, socket device layers, socket syscalls, stat/directory, locking, utilities, vmnt/vnode management, select, and worker threads.

Key contents:
- Includes `request.h`, `threads.h`, `tll.h`, and `type.h`.
- Forward declares major VFS structures to avoid circular includes.
- Declares public entry points for the files in this group: mount/unmount, open/close/lseek/mknod/mkdir, path lookup helpers, pipe suspend/revive helpers, permission checks, read/getdents/rw_pipe, `req_*` wrappers, `sdev_*`, `smap_*`, socket syscalls, and select callbacks.
- Defines endpoint validation convenience macros `okendpt` and `isokendpt`.
- Provides the shared contract surface between syscall dispatch, worker scheduling, request IPC, and vnode/vmnt/file descriptor layers.

Notable details:
- `do_creat` is declared twice in the open section.
- The header exposes many internal subsystem helpers, reflecting the compact monolithic organization of the VFS server.
