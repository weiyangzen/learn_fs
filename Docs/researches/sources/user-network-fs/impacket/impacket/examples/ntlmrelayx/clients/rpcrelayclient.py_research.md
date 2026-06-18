# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/rpcrelayclient.py

## Purpose
`rpcrelayclient.py` relays NTLM authentication to selected DCE/RPC endpoints, currently TSCH and ICPR. It builds custom RPC bind/auth3 packets so ntlmrelayx can validate a relayed identity against RPC services.

## Important APIs, Types, and Functions
`MYDCERPC_v5` provides `sendBindType1()` and `sendBindType3()` with `RPC_C_AUTHN_LEVEL_CONNECT`. `DummyOp` is an `NDRCALL` with opnum 255 used to probe post-auth behavior. `RPCRelayClient` implements endpoint selection, connection setup, NTLM negotiate/auth, keepalive, and disconnect.

## Control Flow
The constructor maps `serverConfig.rpc_mode` to TSCH or ICPR UUID and chooses SMB named pipes or endpoint mapper string bindings. `initConnection()` creates transport, optionally authenticates SMB transport credentials, and connects with the appropriate auth level. `sendNegotiate()` sends NTLM type 1 in an RPC bind and parses the bind-ack challenge. `sendAuth()` sends auth3 with the type 3 token, then issues `DummyOp`; expected operation-range or invalid-header exceptions mean authentication worked, while access denied means failure.

## State and Persistence Behavior
State is the `MYDCERPC_v5` session and selected string binding/UUID. No data is persisted. Keepalive repeats `DummyOp` and expects the same benign exception pattern.

## Dependencies and Integration Points
It depends on Impacket DCE/RPC transport, endpoint mapper, TSCH, ICPR, RPC packet classes, NTLM/SPNEGO parsing, and ntlmrelayx RPC config fields.

## Risks and Edge Cases
Endpoint support is deliberately narrow. The file imports `transport`, `rpcrt`, `epm`, and `tsch` twice and imports `icpr` only in the first duplicated import. `keepAlive()` uses `or` where `and` was likely intended, so exception filtering is suspicious. Success inference relies on service-specific error strings.

## Test Signals
Cover TCP and SMB transports, TSCH and ICPR UUIDs, bind nak/fault paths, SPNEGO unwrap, dummy-op success inference, access denied, and keepalive exception filtering.
