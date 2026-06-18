# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/session.h

This header declares the public session compatibility surface: opaque `struct fuse_session`, `fuse_get_session`, `fuse_session_fd`, `fuse_set_signal_handlers`, and `fuse_remove_signal_handlers`.

Integration points: implemented by `session.c` and used by FUSE 2.5/3.0 compatibility layers. The main risk is representing two conceptual objects, session and fuse, with one underlying pointer.
