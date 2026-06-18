# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/PacketEncryptor.java

Purpose: `PacketEncryptor` wraps SMB2 packets into SMB3 transform packets and decrypts SMB3 encrypted packet data.

Important APIs and control flow: `init` chooses SMB3.1.1 negotiated cipher or AES-128-CCM for older SMB3. `canDecrypt` checks dialect, remaining payload, and algorithm flag. `decrypt` builds AAD from the transform header, decrypts with AEAD, and combines update/final plaintext. `encrypt` returns an `EncryptedPacketWrapper` that serializes plaintext, creates a nonce and transform header, authenticates header fields, encrypts, stores the 16-byte tag as signature, then writes ciphertext.

State, dependencies, and integration: depends on `SecurityProvider`, negotiated dialect/cipher, `SMB2TransformHeader`, and session encryption/decryption keys. Used by `Connection` and `SMB3DecryptingPacketHandler`.

Risks: nonce generation uses `System.nanoTime` and an unused counter, so uniqueness across processes/keys deserves review. AEAD parameter class is `GCMParameterSpec` even for CCM provider abstractions. Tests should cover AAD bytes, encrypt/decrypt round trip, nonce length per cipher, malformed packet rejection, and missing keys.
