# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_client.c

This file implements the 9P client request layer used by p9fs VFS/VOP code.

Core responsibilities:
- Parses mount options into client state, defaulting to `virtio`, `9P2000.L`, and `P9FS_MTU`.
- Allocates/frees request buffers, response buffers, request objects, fids, and tags through UMA zones and `unrhdr` pools.
- Builds 9P request headers, serializes payloads, invokes the transport, parses response headers, and maps `RERROR`/`RLERROR` replies to local errors.
- Maintains transport state: connected, begin-disconnect, disconnected.
- Negotiates protocol version with `Tversion`.
- Creates/destroys clients and transport handles.
- Implements request helpers for attach, walk, open, read, write, readdir, create, remove, unlink, clunk, statfs, renameat, symlink, hardlink, readlink, getattr, and setattr.

Important request lifecycle:
1. `p9_client_request()` calls `p9_client_prepare_req()`.
2. Preparation checks disconnect state, allocates a tagged request, writes the 9P header, writes typed payload fields, and finalizes the size.
3. The selected transport’s `request()` method submits the request and fills the response.
4. `p9_client_check_return()` parses the response header and handles protocol errors.
5. The caller decodes operation-specific response fields and frees the request.

FID behavior:
- `p9_fid_create()` allocates a numeric fid from the client pool and initializes mode/uid.
- `p9_client_attach()` creates a root fid for a user.
- `p9_client_walk()` optionally clones a fid, walks path components, validates returned qid count, and stores the final qid.
- `p9_client_clunk()` sends `Tclunk` when possible, then always destroys the local fid.
- Open/create set `fid->mode` and `fid->mtu`.

I/O behavior:
- `p9_client_read()` and `p9_client_readdir()` cap transfer size by fid MTU, client msize, and caller count.
- Read/write return positive byte counts on success and negative errno values on error.
- `p9_client_read()` treats a zero-byte read as `EIO`.
- `p9_client_write()` caps outgoing data to the server’s accepted size and returns the server write count.

Research-relevant risks:
- Several error paths return immediately after response decode failure and must be audited for request cleanup.
- `p9_client_create()` creates the transport before version negotiation; if negotiation fails, the visible cleanup path frees the client allocation but does not obviously close the transport handle.
- The client state machine permits only `Tclunk` once disconnect begins.
- Serialization/deserialization depends on the format mini-language in `p9_protocol.c`; mismatches can corrupt protocol framing.
