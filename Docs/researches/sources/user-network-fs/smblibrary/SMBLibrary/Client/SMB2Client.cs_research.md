<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB2Client.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB2Client.cs

## Purpose
`SMB2Client` is the stateful SMB2/SMB3 client transport and session manager. It opens Direct TCP or NetBIOS-over-TCP connections, negotiates dialects through SMB 3.1.1, authenticates, tracks credits, signs or encrypts traffic, and exposes high-level share operations.

## Important APIs, Types, And Functions
Important public APIs are constructors, `Connect`, `Disconnect`, `Login`, `Logoff`, `ListShares`, `TreeConnect`, `Echo`, `MaxTransactSize`, `MaxReadSize`, `MaxWriteSize`, `Transport`, and `IsConnected`. Internal integration points include `TrySendCommand`, `WaitForCommand`, and `WaitForSessionResponsePacket`.

## Control Flow
Connection setup resolves or receives an address, opens a socket, optionally performs NetBIOS session establishment, sends `NegotiateRequest`, and records dialect, security blob, signing requirement, maximum sizes, and SMB 3.1.1 preauth state. Login drives an authentication client through one or more `SessionSetupRequest` exchanges, then derives signing/encryption keys. Receive callbacks dequeue NetBIOS session packets, decrypt SMB3 transform packets when needed, parse SMB2 responses, update preauth hash and credits, verify signatures, and signal waiting callers by message ID.

## State And Persistence Behavior
State includes socket/receive buffer ownership, incoming command queue, wait handles, server name, message ID, session ID, negotiated dialect, available credits, signing/encryption keys, preauth hash, authentication blobs, and connection/login booleans. Persistence is network session state only; the class does not write repository or local files.

## Dependencies And Integration Points
Depends on `SMBLibrary.SMB2` packet classes, NetBIOS session packets, socket async receive APIs, `IAuthenticationClient`/NTLM authentication, `SMB2Cryptography`, `ServerServiceHelper`, and `SMB2FileStore` returned from tree connect.

## Risks
Credit accounting is shared mutable state and is not guarded for multiple concurrent request senders. Receive callback disposal races can leave waiters timing out. `Random` is used for SMB 3.1.1 salt rather than a cryptographic RNG. Signature verification is skipped for interim async responses by design, and encrypted sessions bypass header signing. Timeout paths return null rather than rich errors, so callers must map them carefully.

## Test Signals
Signals include integration tests against SMB2/SMB3 servers for Direct TCP and NetBIOS, dialect negotiation including SMB 3.1.1, NTLM login success/failure, signed and encrypted tree connects, credit exhaustion and multi-credit reads/writes, response timeout, invalid signature rejection, and share enumeration through IPC$.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB2Client.cs -->
