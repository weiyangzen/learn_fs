<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/wbc_async.c -->
# sources/user-network-fs/samba/source3/torture/wbc_async.c

## Purpose
`wbc_async.c` implements an asynchronous winbind client transport used by torture tests. It wraps winbind UNIX socket connection setup, nonblocking request/response exchange, optional privileged-pipe upgrade, serialized transaction dispatch through `tevent_queue`, retry handling, and debug callbacks.

## Important APIs, types, and functions
- `map_wbc_err_from_errno()`, `tevent_req_is_wbcerr()`, and `tevent_req_simple_recv_wbcerr()` convert system and tevent errors to `wbcErr`.
- `struct wb_context` holds a `tevent_queue`, active socket fd, privileged-state flag, socket directory, and debug callback.
- `make_nonstd_fd()` and `make_safe_fd()` duplicate descriptors away from stdin/stdout/stderr, set nonblocking mode, and set close-on-exec.
- `wb_context_init()` creates the context and chooses either a caller-supplied socket directory, `SELFTEST_WINBINDD_SOCKET_DIR` under nss-wrapper, or `WINBINDD_SOCKET_DIR`.
- `wb_connect_send/recv()` validates socket directory ownership, validates the socket, creates a safe AF_UNIX stream socket, and performs `async_connect_send`.
- `wb_open_pipe_send/recv()` connects to the nonprivileged pipe, performs an interface-version ping, optionally requests the privileged pipe directory, and reconnects there.
- `wb_trans_send/recv()` queues one winbind request, opens or reuses the pipe, sends with `wb_simple_trans_send`, retries transient failures after one second, and returns a talloc-moved response.
- `wbcSetDebug()`, `wbcSetDebugStderr()`, and `wbcDebug()` provide caller-controlled logging.

## Control flow
Callers allocate a `wb_context`, then submit requests through `wb_trans_send()`. Queue dispatch checks whether the cached fd appears closed with a zero-timeout `select()`, opens a pipe if needed or if privileged access is required, sends the request with the caller's pid, and completes when `wb_simple_trans_recv()` returns a response. Connection setup is a state machine: connect nonprivileged, ping interface version, optionally ask winbind for the privileged directory, close the old fd, reconnect privileged, and mark `is_priv`.

## State and persistence behavior
Runtime state is the cached winbind socket fd and whether it is privileged. Requests are serialized by `tevent_queue`, preventing concurrent writes on one fd. No persistent files are written by this code; it depends on winbindd's socket files and may read an environment variable in selftest mode.

## Dependencies and integration points
The file uses talloc, tevent async requests, `async_connect_send`, winbind protocol structs, `wb_simple_trans_send/recv` from `nsswitch/wb_reqtrans.h`, `set_blocking`, UNIX sockets, and nss-wrapper detection. The header declares additional async ID mapping, PAM, SID, and utility APIs implemented elsewhere.

## Risks and edge cases
- Directory and socket ownership checks allow root or the effective uid only; unusual test setups can fail as winbind unavailable.
- `closed_fd()` treats readable fds as closed, which is a pragmatic health check but can race with peer behavior.
- Transient transaction failures retry forever in one-second increments except for `WBC_ERR_WINBIND_NOT_AVAILABLE`, so a badly wedged daemon can stall callers.
- `strlcpy()` into `sun_path` truncation is not explicitly checked.
- One `wb_context` serializes requests; callers needing parallelism require multiple contexts.

## Test signals
Consumers should observe successful async completion through `wb_trans_recv()` and correct error mapping for unavailable winbind, auth errors, no memory, and unknown failures. Selftests can override the socket directory with `SELFTEST_WINBINDD_SOCKET_DIR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/wbc_async.c -->
