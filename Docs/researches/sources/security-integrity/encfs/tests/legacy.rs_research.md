# sources/security-integrity/encfs/tests/legacy.rs

Purpose: focused legacy V5 decode test that loads a binary `.encfs5` fixture, derives a legacy cipher, decrypts a known encrypted path, and reads/decrypts file contents.

Important APIs/types/functions: `EncfsConfig::load`, `SslCipher::derive_key_legacy`, `EncfsConfig::get_cipher`, `EncFs::new`, `EncFs::decrypt_path`, `SslCipher::decrypt_header`, and `FileDecoder::new/read_at`.

Control flow: locates `tests/fixtures/encfs142/.encfs5`, loads config, prints diagnostic config details, derives legacy key material for visibility, builds `EncFs`, decrypts a hard-coded nested encrypted path, opens the encrypted file, decrypts its 8-byte header using path IV only if external IV chaining is enabled, streams content through `FileDecoder`, and asserts plaintext is valid UTF-8.

State and persistence: reads fixture files only. Output is diagnostic `println!` data for test logs.

Dependencies and integration points: depends on V5 binary config parser, legacy KDF, encrypted fixture path stability, `FileExt::read_at`, and file decoder compatibility with V5 metadata.

Risks: panics if fixture is missing. It checks content validity but not exact expected plaintext, so some semantic regressions could pass if output remains UTF-8.

Test signals: valuable smoke/regression signal for the legacy V5 load/decrypt path and legacy KDF integration.
