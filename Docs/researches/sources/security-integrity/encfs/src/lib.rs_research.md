# sources/security-integrity/encfs/src/lib.rs

Purpose: defines the public library facade for the EncFS crate and centralizes locale initialization. It exposes configuration parsing, constants, crypto, mounted filesystem, reverse filesystem, and process-hardening modules to the binaries and tests.

Important APIs and types: public modules are `config`, `config_binary`, `config_proto`, `constants`, `crypto`, `fs`, `reverse_fs`, and `security`. The main function is `init_locale`, which reads `LANG`, strips encoding suffixes, converts POSIX underscores to BCP-47-style hyphens, and calls `rust_i18n::set_locale`.

Control flow: the module declarations make implementation modules available to `main.rs`, `encfsctl.rs`, `encfsr.rs`, and integration consumers. `init_locale` is called by binaries before translated help/errors are needed; if `LANG` is absent it leaves the rust-i18n fallback in place. Tests load fixtures, construct configs/ciphers, decrypt known filenames and file content, and exercise paranoia-mode path IV behavior through `EncFs::decrypt_path`.

State and persistence behavior: the library facade has no persistent state. `init_locale` mutates rust-i18n global locale state for the current process. The embedded tests read fixture configs and encrypted files from `tests/fixtures` but do not modify them.

Dependencies and integration points: depends directly on `rust_i18n` and, in tests, SHA1, Unix `FileExt`, config loading, filesystem path decryption, and file decoding. It is the import surface used by all three binaries: normal mount uses `config` and `fs::EncFs`, control utility uses `config`, `constants`, and `crypto::ssl`, and reverse mount uses `config`, `reverse_fs`, and `security`.

Risks: locale normalization is simple and assumes `LANG` is enough; unsupported locale keys fall back according to rust-i18n behavior. Because many modules are publicly exported, internal APIs may become de facto external contracts. Fixture tests panic if test fixtures are missing, which is acceptable for local tests but not a graceful skip.

Test signals: `test_decrypt_filenames` verifies a V6 fixture config decrypts a known filename and file content hash. `test_paranoia_mode` verifies chained path IV decryption, nonzero path IV, header decryption with external IV, and the same plaintext SHA1 for paranoia-mode content.
