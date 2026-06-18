<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_named_pipe.c -->
# sources/user-network-fs/samba/source4/samba/service_named_pipe.c

## Purpose

`service_named_pipe.c` adapts the generic stream service layer to Samba named-pipe transports over Unix-domain sockets and named-pipe authentication.

## Important APIs, Types, and Functions

`struct named_pipe_socket` stores pipe name/path, downstream stream ops, and private data. `tstream_setup_named_pipe()` creates the pipe directory and socket listener. `named_pipe_accept()` converts an accepted socket fd into a BSD tstream and starts `tstream_npa_accept_existing_send()`. `named_pipe_accept_done()` completes authentication/session setup and hands the connection to the real pipe server ops.

## Control Flow

The listener is created under `ncalrpc_dir/np`. New stream connections first use `named_pipe_stream_ops`. Accept disables normal fd handling, wraps the socket in tstream, and starts named-pipe-auth negotiation. Completion receives transport type, client/server addresses, names, and `auth_session_info_transport`, builds `conn->session_info`, enforces transport-specific constraints, then swaps `conn->ops` and `private_data` to the downstream server and calls its `accept_connection()`.

## State and Persistence Behavior

The file creates persistent socket path directories and a Unix-domain socket. Per-connection session information is stored in `stream_connection`. No registry or account state is changed.

## Dependencies and Integration Points

It depends on service stream APIs, loadparm `ncalrpc_dir`, auth session conversion, named-pipe-auth tstream helpers, NDR named-pipe auth definitions, and filesystem directory helpers.

## Risks and Edge Cases

It rejects system tokens on `NCACN_NP`, only allows `NCACN_NP` or `NCALRPC`, and terminates connections on any authentication or memory error. Directory permissions are strict for the `np` subdirectory. The temporary named-pipe ops intentionally terminate if raw recv/send handlers are called.

## Test Signals

Tests should cover pipe path normalization with and without `\\pipe\\`, directory creation/permissions, successful NCALRPC and NCACN_NP auth, system-token rejection on remote named pipes, invalid transport rejection, and downstream ops handoff.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_named_pipe.c -->
