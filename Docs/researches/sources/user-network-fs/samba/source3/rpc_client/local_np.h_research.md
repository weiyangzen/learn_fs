# sources/user-network-fs/samba/source3/rpc_client/local_np.h

## Purpose
`local_np.h` declares the API for connecting to local Samba RPC named pipes through `samba-dcerpcd` and authenticated `tstream` transport.

## Important APIs, Types, And Functions
It declares async `local_np_connect_send()`, `local_np_connect_recv()`, and synchronous `local_np_connect()`. Parameters capture pipe name, DCE/RPC transport type, remote/local endpoint identity, auth session info, need-idle-server flag, and output `tstream_context`.

## Control Flow
No logic is implemented in the header. The async contract follows Samba's tevent send/recv pattern; the synchronous helper hides event-context allocation and polling.

## State And Persistence
The header stores no state. The implementation returns an owned `tstream_context` and may start a local helper process.

## Dependencies And Integration Points
It includes tsocket and RPC transport enum declarations, forward-declares `auth_session_info`, and is consumed by local RPC client paths that need named-pipe streams.

## Risks
Callers must keep endpoint/session inputs coherent because they are transmitted to the helper for authorization context. The sync helper can block while connecting/spawning.

## Test Signals
Compile coverage plus local named-pipe connection tests, invalid argument tests, and helper-spawn behavior validate this API.
