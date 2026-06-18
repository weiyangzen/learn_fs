# sources/security-integrity/encfs/tests/fixtures/encfs6-std.xml

Purpose: V6 XML EncFS fixture representing standard mode. It validates baseline compatibility for AES-192, block name encoding, unique IVs, chained name IVs, PBKDF2, and no block MAC overhead.

Important data fields: `version` 20100713, creator `EncFS 1.9.5`, cipher `ssl/aes` major 3, name algorithm `nameio/block` major 4, `keySize` 192, `blockSize` 1024, `plainData` 0, `uniqueIV` 1, `chainedNameIV` 1, `externalIVChaining` 0, `blockMACBytes` 0, `allowHoles` 1, `encodedKeySize` 44, a 20-byte salt, `kdfIterations` 1389869, and `desiredKDFDuration` 500.

Control flow role: loaded by config tests and live mount helpers, then used to derive a cipher with password `test`. Known encrypted names decrypt to fixture plaintext such as `DESIGN.md`, and file contents hash to expected values.

State and persistence: static fixture. It must be kept in sync with encrypted fixture data in the same directory.

Dependencies and integration points: exercises the XML parser, PBKDF2 KDF defaulting, AES-192, `EncFs::decrypt_path`, and file decode without block MAC bytes.

Risks: fixture drift breaks deterministic path/hash assertions. Its high PBKDF2 iteration count can be noticeable in test runtime. Tests assume the password is `test`.

Test signals: primary standard-mode fixture for compatibility, live mount, config backward-compatibility, and reverse-mode tests.
