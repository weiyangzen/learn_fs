# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_transport.h

This header defines the p9fs transport module interface.

Key type:
- `struct p9_trans_module` contains:
  - TAILQ linkage.
  - Transport `name`.
  - `create(mount_tag, handlep)` to establish a connection.
  - `close(handle)` to terminate a connection.
  - `request(handle, req)` to submit a 9P request.
  - `cancel(handle, req)` to cancel an in-flight request.

Exported functions:
- `p9_register_trans()`
- `p9_unregister_trans()`
- `p9_get_trans_by_name()`

Research-relevant notes:
- The transport interface is synchronous from the client’s perspective: `request()` is expected to return with the response buffer populated or an error.
- `struct p9_req_t` is forward-declared here to avoid depending on the full client header.
