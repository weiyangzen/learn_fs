<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/SessionSetupHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/SessionSetupHelper.cs

## Purpose
SMB2 session setup and authentication. It feeds client security tokens to the configured GSS provider, allocates session IDs, handles multi-leg authentication, creates authenticated or guest sessions, and derives SMB2 signing keys.

## APIs, Types, and Functions
`SessionSetupHelper.GetSessionSetupResponse()` is the entry point. It uses `GSSProvider.AcceptSecurityContext()`, context attributes such as user/domain/machine/session key/access token/guest flag, `SMB2Cryptography.GenerateSigningKey()`, and `SMB2ConnectionState.CreateSession()`.

## Control Flow, State, and Persistence
The helper returns an error for authentication failures. Output security tokens are included when present. If the request has no session ID it allocates one even for `STATUS_MORE_PROCESSING_REQUIRED`; if the supplied ID already maps to an established session it rejects the request. On success it truncates long GSS session keys to 16 bytes, honors client signing-required mode, and stores the session in connection state. Guest sessions disable signing and mark `SessionFlags.IsGuest`.

## Dependencies and Integration
Called before tree access by `SMBServer.SMB2.cs`. It integrates with NTLM/Kerberos-capable GSS providers and SMB2 dialect conversion.

## Risks and Test Signals
Risks include shared `state.AuthenticationContext` behavior across simultaneous session setups, null session keys for signing, no SMB3-specific signing/encryption key derivation, and rejecting reauth on existing sessions. Test multi-leg NTLM, bad credentials, guest fallback, signing required, long session keys, too-many-sessions, and duplicate session IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/SessionSetupHelper.cs -->
