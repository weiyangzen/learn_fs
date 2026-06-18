# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB3DecryptingPacketHandler.java

Purpose: `SMB3DecryptingPacketHandler` decrypts SMB3 transform packets before the SMB2 handler chain processes them.

Important APIs and control flow: it handles `SMB3EncryptedPacketData`, validates decryptability, finds the session by transform session ID, decrypts with the session decryption key, inspects the decrypted protocol ID, rejects nested encryption, forwards compressed data as `SMB3CompressedPacketData`, or wraps SMB2 plaintext in `SMB2DecryptedPacketData`. It dead-letters mismatched session IDs.

State, dependencies, and integration: depends on `SessionTable` and `PacketEncryptor`; it is first in the connection incoming chain.

Risks: compressed validation and compounded session ID validation are TODOs. Decryption failures become runtime exceptions from the encryptor. Tests should cover encrypted SMB2, compressed payloads, nested encryption rejection, unknown protocol rejection, missing session, and session ID mismatch.
