# sources/user-network-fs/samba/source4/lib/socket/connect.c

## Purpose

`connect.c` implements event-aware nonblocking socket connect wrappers for Samba's tevent and composite async frameworks.

## Important APIs, Types, and Functions

`struct connect_state` stores the socket, optional local address, server address, and flags. Public APIs are `socket_connect_send()`, `socket_connect_recv()`, and `socket_connect_ev()`. Internal functions are `socket_send_connect()` and `socket_connect_handler()`.

## Control Flow

`socket_connect_send()` creates a composite context, references the socket and addresses, marks the socket fd nonblocking, and calls `socket_send_connect()`. That function calls low-level `socket_connect()`. Immediate fatal errors complete the composite with an error; `NT_STATUS_MORE_PROCESSING_REQUIRED` or success installs a tevent fd handler watching read/write. The handler calls `socket_connect_complete()` and completes the composite on success. `socket_connect_recv()` waits and frees the composite, while `socket_connect_ev()` provides a synchronous wrapper around the async path.

## State and Persistence Behavior

The connect operation state lives under the composite context and holds talloc references to socket/address inputs. The socket fd is left in nonblocking mode. Successful completion leaves the caller's socket connected; failures leave cleanup to the caller and talloc hierarchy.

## Dependencies and Integration Points

It depends on Samba socket APIs, tevent fd events, and `libcli/composite`. `connect_multi.c` builds racing multi-port connects on top of `socket_connect_send()`.

## Risks and Edge Cases

The fd handler is registered for both read and write, but connect completion usually depends on writability; spurious events rely on `socket_connect_complete()` correctness. There is no timeout in this file. If `socket_connect_send()` returns NULL, `socket_connect_ev()` passes NULL to recv, so callers should check allocation failures in direct async use.

## Test Signals

Tests should cover immediate connect success, EINPROGRESS completion, refused connections, unreachable addresses, local bind address use, nonblocking fd state, and event loop cancellation/freeing before completion.

Source-read signal: reviewed complete local file (158 lines).
