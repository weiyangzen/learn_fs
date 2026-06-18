# sources/security-integrity/encfs/tests/fixtures/encfs6-paranoia.xml

Purpose: V6 XML EncFS fixture representing paranoia mode. It is used by compatibility and live tests to validate parsing, PBKDF2 key derivation, external IV chaining, and per-block MAC behavior.

Important data fields: `version` 20100713, creator `EncFS 1.9.5`, cipher `ssl/aes` major 3, name algorithm `nameio/block` major 4, `keySize` 256, `blockSize` 1024, `uniqueIV` 1, `chainedNameIV` 1, `externalIVChaining` 1, `blockMACBytes` 8, `allowHoles` 1, `encodedKeySize` 52, a 20-byte salt, `kdfIterations` 5711682, and `desiredKDFDuration` 3000.

Control flow role: the fixture is consumed by `EncfsConfig::load`; tests then derive a cipher with password `test`, decrypt known encrypted paths, use path IVs for file header decryption, and verify plaintext hashes or live mount behavior.

State and persistence: static fixture. It should remain byte-stable because expected hashes and encrypted filenames depend on its key material and mode bits.

Dependencies and integration points: integrates with V6 XML parser, AES-256 OpenSSL setup, PBKDF2, block-name decoding, `FileDecoder`, and `EncFs` external IV handling.

Risks: accidental edits break broad compatibility tests. High KDF iteration count can make tests slower. Because it contains test key material, it must not be mistaken for production secret handling.

Test signals: central fixture for paranoia mode tests in `config_compatibility.rs`, `live_mount.rs`, and reverse round-trip setup.
