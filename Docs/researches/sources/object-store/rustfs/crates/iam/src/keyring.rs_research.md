# sources/object-store/rustfs/crates/iam/src/keyring.rs

`keyring.rs` loads IAM master keys from environment variables for encrypt-current/decrypt-many key rotation. `ENV_IAM_MASTER_KEY` is the active encryption key and `ENV_IAM_MASTER_KEY_OLD_KEYS` is a comma-separated list of legacy decrypt keys. `Keyring` stores an optional current key and ordered decrypt keys.

`normalize_key` trims empty input away, `parse_old_keys` trims comma-separated legacy keys and skips empty items, `push_unique_key` deduplicates while preserving order, and `build_keyring` places the current key first followed by unique old keys. Public functions are `encrypt_key`, `decrypt_keys`, and `current_key_and_old_keys`; each reads the environment and rebuilds the keyring rather than caching.

There is no persistent state in this module. It integrates with IAM crypto/store code through byte-vector keys. Risks are lack of key length/encoding/entropy validation and possible inconsistent views if environment variables change between calls. Tests cover parsing, ordering, deduplication, and old-key-only behavior.
