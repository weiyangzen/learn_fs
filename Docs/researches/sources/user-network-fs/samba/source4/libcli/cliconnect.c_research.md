# sources/user-network-fs/samba/source4/libcli/cliconnect.c

## Purpose

`cliconnect.c` provides convenience wrappers for SMB1 client connection setup and teardown. It connects a socket, negotiates protocol, performs session setup, tree-connects to a share, builds a full `smbcli_state`, disconnects a tree, initializes state, and parses UNC names.

## Important APIs, Types, and Functions

Exports include `smbcli_socket_connect()`, `smbcli_negprot()`, `smbcli_session_setup()`, `smbcli_tconX()`, `smbcli_full_connection()`, `smbcli_tdis()`, `smbcli_state_init()`, and `smbcli_parse_unc()`. The helper `terminate_path_at_separator()` splits mutable UNC components.

## Control Flow

The classic sequence is socket connect through `smbcli_sock_connect()`, transport initialization and `smb_raw_negotiate()`, session allocation and `smb_composite_sesssetup()`, then tree allocation and `smb_raw_tcon()`. `smbcli_full_connection()` delegates to `smbcli_tree_full_connection()` and wraps the returned tree/session/transport in a `smbcli_state`. `smbcli_tconX()` chooses password encoding based on negotiated security mode and enables session-key protection when extended signatures are returned.

## State and Persistence Behavior

`smbcli_state` owns or references socket, transport, session, and tree objects under talloc. Successful negotiation consumes `cli->sock` into `cli->transport`. Tree connect persists the TID and session VUID in client state. No server-side data is modified except normal authentication/session/share connection state.

## Dependencies and Integration Points

The file depends on `libcli/libcli.h`, raw SMB1 client APIs, authentication helpers, SMB composite session setup, resolve/loadparm/tevent contexts, and smbXcli session signing helpers.

## Risks and Edge Cases

`smbcli_tconX()` can leak `mem_ctx` on an early invalid short challenge return. Share-level password handling is legacy-sensitive. `smbcli_parse_unc()` mutates allocated copies and only accepts `//` or `\\` prefixes with both server and share. The wrapper returns booleans in some places and NTSTATUS in others, requiring callers to retrieve detailed errors from lower layers.

## Test Signals

Connection tests should cover user-level and share-level security, encrypted share passwords, extended signatures, failed negotiate/session/tree-connect paths, full connection cleanup, and UNC parsing for slash and backslash separators.
