<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB1Client.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB1Client.cs

## Purpose
`SMB1Client` implements the `ISMBClient` lifecycle for SMB1/CIFS over direct TCP or NetBIOS-over-TCP.

## Important APIs and Types
Public APIs cover connection, login with selected NTLM method, logoff, share listing, tree connect, echo, and negotiated max read/write sizes. Internal helpers include dialect negotiation, NetBIOS name fallback, asynchronous socket receive processing, message wait queues, and SMB1 packet sending.

## Control Flow
`Connect()` resolves addresses, opens a socket, optionally performs NetBIOS session setup, then negotiates the `NT LM 0.12` dialect. Non-extended security stores a raw server challenge; extended security stores the server security blob. `Login()` builds client capabilities and either sends legacy `SessionSetupAndXRequest` with LM/NT responses or runs a SPNEGO/NTLM loop using `NTLMAuthenticationClient` until success or error. Received packets are asynchronously decoded into SMB1 messages and enqueued; synchronous operations wait for matching command responses with a timeout.

## State, Dependencies, and Integration
The client owns socket state, negotiated capabilities, user ID, session key, incoming queues, and NetBIOS session response state. It creates `SMB1FileStore` for tree operations and uses `ServerServiceHelper` over `IPC$` for share enumeration.

## Risks and Test Signals
Request matching only checks command name, not MID/PID, while max multiplex count is forced to 1. Random client challenges use `Random`. Logoff sets `m_isLoggedIn` to status-not-success, likely inverted. Tests should cover both transports, dialect capability parsing, legacy and extended-security login, timeout/disconnect behavior, queue matching, tree connect, and logoff state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB1Client.cs -->
