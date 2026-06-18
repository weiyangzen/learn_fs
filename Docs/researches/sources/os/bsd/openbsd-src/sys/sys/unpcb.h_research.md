# File Research: sources/os/bsd/openbsd-src/sys/sys/unpcb.h

Defines UNIX-domain socket protocol control blocks. `struct unpcb` links a socket to an optional filesystem vnode, connected peer, referrer list, bound address, file backpointer for GC, fake inode, peer credentials, creation time, and per-AF socket list. Lock annotations identify immutable, socket-lock, and GC-lock protected fields.

Kernel declarations cover attach/detach, bind/listen/connect/accept/disconnect/shutdown/send/receive, address queries, socket stat, peer connection, garbage collection, and internalize/externalize/dispose of file descriptors in control messages. This is a key socket/VFS bridge because pathname sockets hold vnode references.
