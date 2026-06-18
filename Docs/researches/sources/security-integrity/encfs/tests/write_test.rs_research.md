# sources/security-integrity/encfs/tests/write_test.rs

Purpose: basic direct-driver write test for `EncFs`, validating create/write/reopen persistence by decrypting the physical encrypted file manually.

Important APIs/types/functions: constructs `EncfsConfig`, `SslCipher`, and `EncFs`; uses `create`, `write`, `release`, `open`; verifies via `FileExt::read_at`, `SslCipher::decrypt_header`, and `FileDecoder`.

Control flow: creates temp root, configures AES-192 with deterministic key/IV and MAC bytes 8, creates `test.txt`, writes `hello world`, locates the encrypted file, decrypts the header with external IV 0, decodes content, releases the handle, opens the virtual path again, and re-decodes to ensure persistence.

State and persistence: writes one encrypted backing file and removes the temp root.

Dependencies and integration points: validates the write path, file header generation, block MAC layout, and path encryption enough for reopen.

Risks: verification locates the first backing entry rather than deriving the encrypted path. It tests a single small write and does not cover partial overwrite or multi-block behavior.

Test signals: foundational smoke test for encrypted write/readback at the trait level.
