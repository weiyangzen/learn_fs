# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SMBSessionBuilder.java

Purpose: `SMBSessionBuilder` establishes authenticated SMB sessions and derives session cryptographic keys.

Important APIs and control flow: `establish` selects an authenticator compatible with server mech types and the auth context, optionally wraps NTLM with `NtlmSealer`, initializes it, processes tokens, and recursively calls session setup until success. `setupSession` handles `STATUS_MORE_PROCESSING_REQUIRED`, maintains SMB3.1.1 preauth sessions, updates preauth hashes, processes final tokens, installs the session key, validates signing rules, derives signing/encryption/decryption/application keys, marks the context established, and registers the session.

State, dependencies, and integration: uses `Connection`, `ConnectionContext`, session tables, configured authenticator factories, SPNEGO token classes, security provider KDF/digest, and `SessionFactory`.

Risks: recursive setup depends on authenticator eventually completing. Signing rules for guest/null/encrypted sessions are protocol-sensitive. KDF labels and preauth context must match SMB dialect. Tests should cover authenticator selection, multi-round NTLM/SPNEGO, guest signing rejection, SMB3.1.1 preauth hash updates, key derivation vectors, failed statuses, and preauth table cleanup.
