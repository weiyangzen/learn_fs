# sources/sync-backup/borg/docs/usage/repo-create.rst.inc

Purpose: Documents `borg repo-create`, which initializes a new empty Borg repository and selects its encryption/authentication mode and key location.

Important APIs/types/functions: CLI contract is `borg [common options] repo-create [options]`. Important options are required `--encryption MODE`, `--key-location LOCATION`, `--other-repo SRC_REPOSITORY`, `--from-borg1`, and `--copy-crypt-key`. Documented encryption modes include BLAKE3/ChaCha20/Poly1305, AES-OCB, authenticated modes, and `none`.

Control flow: Runtime creates the store, generates or reuses key material, asks for a passphrase when applicable, derives key encryption key, encrypts/signs the Borg key, stores it in repository or keyfile location, and initializes repository metadata. Related repository creation imports selected secrets from another repo for deduplication/transfer.

State and persistence: Creates persistent repository structure and key material. Encryption mode is immutable after creation; only key location/passphrase can be changed later.

Dependencies and integration points: Depends on `borgstore` backends, crypto primitives, key export/import/change commands, `benchmark cpu`, and `transfer` for related repositories and Borg 1 migration.

Risks: Weak passphrases, `none` mode, or losing keys can compromise confidentiality or availability. Reusing crypt keys with `--copy-crypt-key` changes key management tradeoffs. Remote stores may be slow due to pre-created directories.

Test signals: Tests should cover all encryption modes, key locations, passphrase prompts, `none` mode no-key behavior, related repository creation, `--from-borg1` compatibility, `--copy-crypt-key`, and subsequent transfer/deduplication behavior.
