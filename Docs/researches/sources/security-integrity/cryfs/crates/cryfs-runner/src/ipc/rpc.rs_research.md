# sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/rpc.rs

## Purpose
Builds typed request/response RPC abstractions over two unidirectional `pipe.rs` channels.

## Important APIs, types, and functions
- `RpcConnection::new_pipe` creates request and response pipes.
- `into_client_and_child_fds` keeps parent-side client ends and returns child fd ownership for spawn mapping.
- Test-only `into_server_and_client` splits an in-process server/client pair.
- `RpcServer::from_raw_fds`, `next_request`, `send_response`, and `send_raw_handshake`.
- `RpcClient::send_request`, `recv_response`, and raw handshake receive.

## Control flow
Connection setup creates two typed pipes. Parent/child spawn conversion assigns request sender plus response receiver to the client and request receiver plus response sender to the child. The daemon reconstructs `RpcServer` from fds 3 and 4. Raw handshakes bypass postcard but still use pipe framing and must happen before typed RPC.

## State and persistence behavior
State is owned pipe endpoints. There is no disk persistence.

## Dependencies and integration points
Uses `Sender`/`Receiver` from `pipe.rs`, serde bounds, `OwnedFd`/`RawFd`, and `anyhow`. It is the core transport for background daemon bootstrap and mount RPC.

## Risks and edge cases
`RpcServer::from_raw_fds` is unsafe because fd numbers must be valid, owned pipe ends and must not be reconstructed twice. Schema mismatches between parent and daemon are mitigated by spawn's build-id handshake before typed deserialization.

## Test signals
The unit test verifies a request/response round trip over a local connection. Broader daemon tests validate fd mapping, EOF, and handshakes.
