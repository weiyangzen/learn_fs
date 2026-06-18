# File Research: sources/local-fs/ocfs2-tools/include/o2cb/o2cb_client_proto.h

This header defines the userspace client protocol interface for OCFS2/O2CB control daemons.

Key content:
- Defines line length, argument count, and socket path constants for `ocfs2_controld` and `o2cb_controld`.
- Enumerates client messages such as mount, mount result, unmount, status, list filesystems, list mounts, list clusters, item count/item, and dump.
- Declares socket listen/connect helpers.
- Provides inline helpers for OCFS2 controld listen/connect.
- Declares message send/receive, full receive with rest string, received-list free, list receive, and status parse helpers.

Integration notes:
- This is protocol-facing API; implementations live outside this header.
