# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/PacketSignatoryTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/PacketSignatoryTest.java

Purpose: tests SMB packet signing. It verifies signature generation and verification behavior for selected dialect/security settings, using known packet data and signing keys.

State and persistence: in-memory keys and packets only. Dependencies are signing algorithms, SMB2 headers, security provider, and JUnit. Integration point is message integrity for authenticated SMB sessions. Risks covered include zeroing the signature field before signing, dialect-specific algorithm selection, session binding, and verification failures. Test signal is important for security regressions but limited to fixture vectors.
