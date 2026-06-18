# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/PacketEncryptorTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/PacketEncryptorTest.java

Purpose: tests SMB packet encryption behavior. It validates `PacketEncryptor` output headers/body transformation using fixed keys, nonce/signature fields, dialect/session context, and expected encrypted/decrypted packet data.

State and persistence: transient crypto keys and packet buffers only. Dependencies are SMB3 transform header/message classes, security provider crypto primitives, and JUnit. Integration point is SMB 3.x encrypted sessions. Risks covered include nonce handling, transform header fields, algorithm selection, session-id binding, and ciphertext/authentication tag correctness. Test signal is high-value for interoperability and security.
