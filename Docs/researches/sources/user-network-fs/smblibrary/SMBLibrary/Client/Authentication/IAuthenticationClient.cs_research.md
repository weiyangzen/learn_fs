<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Authentication/IAuthenticationClient.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Authentication/IAuthenticationClient.cs

## Purpose
`IAuthenticationClient` abstracts client-side security context negotiation for SMB session setup.

## Important APIs and Types
`InitializeSecurityContext(byte[] securityBlob)` consumes a server security blob and returns the next credentials blob, or null for invalid input. `GetSessionKey()` returns the negotiated session key. `ResetSecurityContext(string spn)` prepares the same credentials for another server/SPN, primarily DFS.

## Control Flow
Implementations are expected to be stateful: first call emits an initial token, later calls consume challenges and emit authenticators.

## State, Dependencies, and Integration
`NTLMAuthenticationClient` implements this contract for SMB1 extended security and likely SMB2 clients elsewhere. DFS logic can reset SPN-specific context without recreating credentials.

## Risks and Test Signals
The interface does not expose completion state or error details beyond null. Tests for implementers should cover first-call/second-call sequencing, null or malformed blobs, session-key availability only after success, and SPN reset behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Authentication/IAuthenticationClient.cs -->
