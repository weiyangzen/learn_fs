# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/smbrelayclient.py

## Purpose
`smbrelayclient.py` is the SMB relay target client. It negotiates SMB1 or SMB2/3 with a target, relays NTLMSSP session setup messages, supports standard security for reflection, and can derive signing keys through Netlogon for remove-target/MIC scenarios.

## Important APIs, Types, and Functions
`MYSMB` and `MYSMB3` customize negotiation to respect extended security and avoid signing. `SMBRelayClient` implements `initConnection()`, `sendNegotiate()`, SMB1/SMB2 negotiate/auth variants, `sendStandardSecurityAuth()`, `netlogonSessionKey()`, `getStandardSecurityChallenge()`, `isAdmin()`, and keepalive.

## Control Flow
`initConnection()` manually negotiates dialects, chooses SMB1 vs SMB2/3, and wraps the low-level connection in `SMBConnection`. `sendNegotiate()` optionally strips MIC-related flags, relays type 1 through SMB1 SessionSetupAndX or SMB2 SESSION_SETUP, stores the challenge in `sessionData`, and records the server challenge. `sendAuth()` optionally strips MIC fields, handles `remove_target` by validating over Netlogon and recalculating the MIC, then sends SMB1 or SMB2 type 3 auth. Standard-security auth sends ANSI/Unicode password fields directly.

## State and Persistence Behavior
The client retains `sessionData`, negotiate/challenge bytes, server challenge, keepalive hit count, machine account settings, and an active SMBConnection. Successful remove-target mode installs a signing key on the underlying SMB connection. No local files are written by this client.

## Dependencies and Integration Points
It integrates deeply with Impacket SMB, SMB3, SMBConnection, SPNEGO, NRPC, SCMR, DCERPC transport, ntlmrelayx SOCKS keepalive timing, and config flags for SMB2 support, remove_mic, remove_target, machineAccount, machineHashes, and domainIp.

## Risks and Edge Cases
Signing-required targets stop the attack unless a compatible bypass is enabled. Manual packet construction touches private SMB internals and dialect-specific status handling. Netlogon-derived signing relies on configured machine credentials. `isAdmin()` opens SCMR and treats failures broadly.

## Test Signals
Test SMB1, SMB2.002, SMB2.1, SMB3 negotiation, signing-required rejection, remove_mic and remove_target modes, standard-security reflection, Netlogon signing key installation, IPC$ keepalive, and SCMR admin detection.
