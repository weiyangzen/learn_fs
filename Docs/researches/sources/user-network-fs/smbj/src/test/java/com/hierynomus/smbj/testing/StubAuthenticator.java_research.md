# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/StubAuthenticator.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/StubAuthenticator.java

Purpose: authentication test double for SMB session setup. It provides a factory and authenticator implementation that can satisfy SMBJ authentication flows without real NTLM/Kerberos negotiation.

State and persistence: minimal in-memory factory/authenticator state; no credential persistence. Dependencies are SMBJ authenticator interfaces, authentication context, and session setup message types. Integration point is connection/session tests that need a successful login path. Risks include masking real authentication edge cases and hard-coding success behavior. Test signal is helper-level; it enables deterministic tests of connection/share logic independent of crypto auth.
