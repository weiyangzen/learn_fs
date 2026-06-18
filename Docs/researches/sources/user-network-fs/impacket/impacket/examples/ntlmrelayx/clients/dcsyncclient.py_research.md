# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/dcsyncclient.py

## Purpose
`dcsyncclient.py` implements the `DCSYNC` relay target client. It relays a captured NTLM exchange directly into DRSUAPI, then uses Netlogon/Zerologon-style validation to derive the DCE/RPC signing and sealing key needed for directory replication calls and `secretsdump`-style NTDS extraction.

## Important APIs, Types, and Functions
`MYDCERPC_v5` extends `DCERPC_v5` with `sendBindType1()` and `sendBindType3()` so the relay can inject NTLM type 1 and type 3 blobs into RPC bind/auth3 packets at packet privacy level. `PatchedRemoteOperations` bypasses SAMR setup when no SMB credentials are supplied. `DCSYNCRelayClient` exposes the ntlmrelayx client contract: `initConnection()`, `sendNegotiate()`, `sendAuth()`, `netlogonSessionKey()`, `killConnection()`, and `keepAlive()`.

## Control Flow
Construction resolves the DRSUAPI string binding through endpoint mapper. `initConnection()` builds a DCE/RPC transport, optionally authenticating its transport over SMB with configured RPC SMB credentials. `sendNegotiate()` parses the incoming NTLM negotiate, forces seal support, sends an RPC bind with NTLM type 1, and returns the target challenge. `sendAuth()` unwraps SPNEGO when needed, obtains the sign/seal key through `netlogonSessionKey()`, recalculates the NTLM MIC, sends auth3, performs `DRSBind`, initializes `RemoteOperations`, discovers the NTDS DSA object GUID, and invokes `NTDSHashes.dump()` for all users or selected high-value accounts.

## State and Persistence Behavior
The client mutates `self.session` private signing/sealing fields and RC4 handles directly after Netlogon validation. It stores the negotiated message and challenge for MIC recalculation. Dump output is written through `NTDSHashes` using the hard-coded output prefix `hashes`; `RemoteOperations.finish()` is called in `finally`.

## Dependencies and Integration Points
It depends on Impacket NTLM/SPNEGO, DCE/RPC endpoint mapper, DRSUAPI, NRPC, SMBConnection, and `examples.secretsdump`. It integrates with ntlmrelayx protocol registration through `PROTOCOL_CLIENT_CLASS` and with RPC options such as `rpc_mode`, `rpc_use_smb`, and SMB credential fields on `serverConfig`.

## Risks and Edge Cases
This client is tightly coupled to vulnerable or specially configured Netlogon behavior, NTLMv2 AV pairs, DCE/RPC private attributes, and target DRS permissions. It prints tracebacks on exceptions and may leave partial hash output. NTLMv1 is rejected, patched Zerologon targets fail after many attempts, and DRS extension epoch mismatch requires a second bind.

## Test Signals
Use controlled lab DCs to test successful type1/type3 DRS bind, NTLM MIC recalculation, Netlogon failure paths, NTLMv1 rejection, SMB-credential and no-SMB modes, and `RemoteOperations.finish()` cleanup after exceptions.
