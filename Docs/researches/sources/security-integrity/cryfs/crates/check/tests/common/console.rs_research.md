## sources/security-integrity/cryfs/crates/check/tests/common/console.rs

Purpose: provides a deterministic `Console` implementation used only while creating fixture config. It avoids interactive prompts and supplies fixed cryptographic/filesystem parameters.

Important APIs and functions: `FixtureCreationConsole` implements `cryfs_config::config::Console`. Only three methods are expected to be used: `ask_scrypt_settings_for_new_filesystem` returns `ScryptSettings::TEST`, `ask_cipher_for_new_filesystem` returns `aes-256-gcm`, and `ask_blocksize_bytes_for_new_filesystem` returns 104 bytes. Migration, replacement, key-change, single-client, and path-creation prompts panic as unused.

Control flow and state: there is no persistent state. The fixture’s config creation calls this console to obtain repeatable values; every unexpected prompt fails the test immediately.

Dependencies and integration: depends on `anyhow`, `byte_unit::Byte`, `cryfs_crypto::kdf::scrypt`, and `cryfs_version` types required by the `Console` trait. It integrates with `FixtureTempDir::create_config` in `fixture.rs`.

Risks and test signals: the tiny block size is deliberate because corruption tests need many nodes from moderate test payloads. Panicking unused prompts are a useful guard: if config creation starts requiring new user decisions, tests fail rather than silently accepting defaults.
