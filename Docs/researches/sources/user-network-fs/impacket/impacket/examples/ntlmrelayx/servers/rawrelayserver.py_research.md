# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/rawrelayserver.py

## Purpose
`rawrelayserver.py` provides a minimal length-prefixed NTLM relay listener for third-party integrations. It accepts raw NTLM type 1/type 3 blobs over TCP and bridges them into ntlmrelayx protocol clients and attacks.

## Important APIs, Types, and Functions
`RAWRelayServer` wraps nested `RAWServer` and `RAWHandler`. The handler implements `handle()`, `do_ntlm_negotiate()`, `do_ntlm_auth()`, and `do_attack()`.

## Control Flow
On connection, the handler creates a reflection target if none is configured, selects a target, then reads a two-byte signed length and NTLM negotiate blob. It initializes the target protocol client, forwards type 1, optionally removes target NetBIOS AV pair, sends the raw challenge back with a length prefix, reads type 3, relays auth, sends a one-byte boolean success result, records John hash output, registers target success, and starts SOCKS or attack handling.

## State and Persistence Behavior
Per-connection state includes selected target, relay client, challenge, and auth user. Successful relays may write hash output and enqueue `activeConnections`. There is no protocol-level session persistence beyond the live socket/client.

## Dependencies and Integration Points
It depends on `socketserver`, Impacket NTLM, SMB hash-output helpers, `TargetsProcessor`, configured protocol clients/attacks, and SOCKS active connection queue.

## Risks and Edge Cases
The two-byte signed length limits token size and lacks robust partial-read handling. There is no authentication or framing beyond simple lengths, so callers must be trusted. Anonymous auth is rejected except localhost-target special handling.

## Test Signals
Test valid type1/type3 exchanges, fragmented raw reads, target exhaustion, reflection target creation, remove_target AV stripping, anonymous rejection, hash output, and SOCKS/attack dispatch.
