# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/NtlmSealer.java

Purpose: `NtlmSealer` wraps `NtlmAuthenticator` to add NTLM Extended Session Security signing/sealing for SPNEGO mech-list MIC.

Important APIs and control flow: it delegates authentication, derives signing and sealing keys from the exported session key when present, records negotiated mech types from `NegTokenInit`, and on `NegTokenTarg` signs the DER-encoded mech list using a sequence number. If key exchange is negotiated, it RC4-encrypts the signature before storing it as mech-list MIC.

State, dependencies, and integration: it stores derived keys, an atomic sequence number, mech types, wrapped authenticator, and security provider. `SMBSessionBuilder` inserts this wrapper when NTLM integrity is enabled.

Risks: only client-to-server constants are implemented. `mechTypes` must be captured before signing target tokens. Legacy sealing key branches depend on Windows version. Tests should cover wrapper selection, DER mech-list signing, sequence increment, key-exchange encryption, and no-op behavior before session key exists.
