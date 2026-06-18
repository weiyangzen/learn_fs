# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_secondary.c

## Purpose

`dcerpc_secondary.c` creates secondary DCE/RPC connections or authenticated secondary pipes from an existing primary pipe. It is used for authentication fallbacks, basis connections in Python bindings, and multi-context/multi-pipe workflows that must reuse transport context.

## Important APIs, Types, and Functions

`struct sec_conn_state` carries primary pipe, new pipe, and duplicated binding. `struct sec_auth_conn_state` wraps secondary connection plus bind/auth state. Public APIs are `dcerpc_secondary_connection_send/recv()`, `dcerpc_secondary_auth_connection_send/recv()`, and synchronous `dcerpc_secondary_auth_connection()`. Transport callbacks include `continue_open_smb()`, `continue_open_tcp()`, `continue_open_ncalrpc()`, `continue_open_ncacn_unix()`, and `continue_pipe_open()`.

## Control Flow

The send path duplicates the supplied binding, initializes a second pipe on the same event context, fills missing host, target hostname, endpoint, local address, or ncalrpc directory from the primary binding, and dispatches by the primary connection transport. SMB named pipes reuse the SMB connection/session/tcon, TCP requires an IP host and endpoint port, ncalrpc builds a Unix-socket path from the ncalrpc directory and endpoint, and Unix stream opens the endpoint path directly. Successful opens copy flags and binding to the new pipe.

## State and Persistence Behavior

No persistent storage is used. The new pipe is allocated under the composite context, then stolen under the primary pipe or caller memory on receive. TCP open updates the duplicated binding's `localaddress` and `host` to the actual local and remote addresses.

## Dependencies and Integration Points

This code depends on `dcerpc_smb.c`, `dcerpc_sock.c`, binding helpers, resolve context setup, composite async contexts, and `dcerpc_pipe_auth_send()` from `dcerpc_util.c`. It is directly used by schannel setup, auth fallback from SPNEGO to NTLMSSP, Python basis connections, and other callers needing a second pipe.

## Risks and Test Signals

Risks include missing endpoint/host fallback, rejecting non-IP TCP hostnames in secondary paths, talloc ownership mistakes when auth fallback replaces the original pipe, and transport-specific option propagation. Tests should cover secondary pipes for `ncacn_np`, `ncacn_ip_tcp`, `ncalrpc`, and `ncacn_unix_stream`, plus authenticated secondary binds with and without credentials.
