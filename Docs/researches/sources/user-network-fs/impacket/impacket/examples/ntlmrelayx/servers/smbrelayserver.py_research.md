# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/smbrelayserver.py

## Purpose
`smbrelayserver.py` implements the SMB listener side of ntlmrelayx. It hooks Impacket's SMB server to capture SMB1/SMB2 NTLM authentication, relay it to configured targets, and use tree-connect reconnect semantics for multirelay.

## Important APIs, Types, and Functions
`SMBRelayServer` configures an `SMBSERVER` with IPC$, hooks SMB1 and SMB2 negotiate/session-setup/tree-connect commands, and implements `init_client()`, `do_ntlm_negotiate()`, `do_ntlm_auth()`, `do_attack()`, `_start()`, and `run()`. `auth_callback()` logs pre-relay identities in multirelay mode.

## Control Flow
Initialization builds an SMB server config, installs command hooks, and stores a relay connection. In disableMulti mode negotiate immediately selects and initializes a target client. In multirelay mode the original SMB server first authenticates locally; tree connect then selects a target, stores `SMBClient`, clears previous auth state, and returns `STATUS_NETWORK_SESSION_EXPIRED` so the client reauthenticates. Session setup unwraps SPNEGO/raw NTLM, forwards type 1 to the target, returns the challenge, forwards type 3, logs success/failure, records hash output, registers target status, then dispatches SOCKS or an attack thread.

## State and Persistence Behavior
State is stored both on the server object (`target`, `targetprocessor`, `authUser`) and Impacket connection data (`SMBClient`, `NEGOTIATE_MESSAGE`, `CHALLENGE_MESSAGE`, `AUTHENTICATE_MESSAGE`, `relayToHost`, `Authenticated`, `EncryptionKey`, `Uid`). Hash output may be written through SMB server config.

## Dependencies and Integration Points
It depends on Impacket SMB/SMB3/SMBSERVER, SPNEGO, target processing, SOCKS active connections, configured protocol clients/attacks, and ntlmrelayx options for SMB2, reflection, disableMulti, keepRelaying, ADCS, dump hashes, and output files.

## Risks and Edge Cases
This file is highly stateful and mutates per-connection dictionaries. Fixed SMB1 UID `10`, reconnect loops, SPNEGO/raw token differences, signing, reflection downgrades, and target exhaustion are fragile areas. Exceptions inside hooks can terminate client sessions abruptly.

## Test Signals
Cover SMB1 extended and standard security, SMB2 negotiation/session setup/tree connect, disableMulti vs multirelay, reflection mode, target reload, raw NTLM and SPNEGO, STATUS_NETWORK_SESSION_EXPIRED loops, hash output, SOCKS queuing, and attack dispatch.
