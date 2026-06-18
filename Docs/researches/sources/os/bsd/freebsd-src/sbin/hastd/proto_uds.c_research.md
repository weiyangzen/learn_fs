# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto_uds.c

`proto_uds.c` implements the `uds` protocol backend for HAST's generic `proto` abstraction using UNIX domain stream sockets. It registers itself with `proto_register()` from a constructor.

The file parses `uds://`, `unix://`, and bare absolute-path addresses into `sockaddr_un`, creates client and server sockets, binds/listens with pre-bind `unlink()`, accepts worker connections, and exposes descriptor/local/remote address helpers. Data transfer is delegated to `proto_common_send()` and `proto_common_recv()`, so ancillary file-descriptor passing is preserved through the common protocol layer.

Important lifecycle detail: listening sockets record an owner PID and only unlink their socket path during close when still in the owning process and still on the server-listen side. Client timeout hooks are mostly placeholders: `uds_connect()` ignores the timeout except for assertions, and `uds_connect_wait()` returns success.
