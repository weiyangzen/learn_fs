# sources/user-network-fs/nfs-utils/support/reexport/fsidd.c

Purpose: `fsidd.c` is the AF_UNIX service daemon that serializes access to the reexport fsid database and exposes a small text command protocol.

Important APIs and control flow: `main` reads `nfs.conf`, initializes the backend, binds a `SOCK_SEQPACKET` socket from `reexport/fsidd_socket`, creates a libevent base, and accepts clients. `client_cb` handles `get_fsidnum`, `get_or_create_fsidnum`, `get_path`, and `version`, returning `+ result` or `- reason`. `srv_cb` accepts clients as nonblocking and installs persistent read events.

State, dependencies, and integration: Global `evbase` and `dbbackend` own process state. The default socket is an abstract namespace path from `FSID_SOCKET_NAME`. It integrates with `reexport.c` clients and `fsidd.service`.

Risks and test signals: `accept4` errors are not checked before `event_new`, request paths are trusted as raw text without newline/protocol escaping, and some server errors return empty success. Tests should cover concurrent clients, abstract and filesystem sockets, bad commands, malformed fsids, backend failure, long paths near `PATH_MAX`, and daemon restart while clients reconnect.
