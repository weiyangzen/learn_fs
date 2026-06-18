# sources/security-integrity/encfs/tests/open_trunc_test.rs

Purpose: regression test for opening an existing encrypted file with `O_TRUNC`; the implementation must regenerate a valid 8-byte file header immediately and allow subsequent writes to decrypt correctly.

Important APIs/types/functions: directly uses `EncFs::create`, `write`, `release`, and `open` with `O_WRONLY | O_TRUNC`. Verification uses a separate `SslCipher`, `FileExt::read_at`, `SslCipher::decrypt_header`, and `FileDecoder`.

Control flow: creates a file, writes initial data, releases it, finds the encrypted backing file, asserts it is larger than the header, opens the virtual path with truncate flags, asserts physical size is exactly 8 bytes, writes new data, releases, decrypts the regenerated header and content, and compares plaintext with new data.

State and persistence: writes temporary encrypted backing data and removes the temp root.

Dependencies and integration points: validates interaction among open flags, header generation, file truncation, block encoding, and decoder compatibility.

Risks: finds the physical file by taking the first directory entry, which assumes only one backing file. Uses deterministic test keys and default config with external IV disabled.

Test signals: strong guard against corrupting empty/truncated encrypted files or leaving missing/zero headers after `O_TRUNC`.
