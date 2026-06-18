# sources/sync-backup/borg/src/borg/archiver/key_cmds.py

## Purpose

`key_cmds.py` implements `borg key`, managing repository key passphrases, additional Borg keys, key listing/removal, key storage location changes, and key export/import. It is a security-sensitive command group operating on key material and key metadata. The source was read as a complete 354-line file.

## Important APIs, Types, and Functions

`KeysMixIn` defines `do_key_change_passphrase()`, `do_key_add()`, `do_key_remove()`, `do_key_list()`, `do_key_change_location()`, `do_key_export()`, and `do_key_import()`. `build_parser_keys()` registers nested subcommands: `export`, `import`, `change-passphrase`, `add`, `remove`, `list`, and `change-location`. Important dependencies are `KEY_LOCATIONS`, `KeyManager`, `Manifest`, `PathSpec`, and `CommandError`.

## Control Flow

Passphrase/add/remove/list/change-location commands open the repository with manifest and check compatibility, then inspect whether the loaded key exposes the needed capability method (`change_passphrase`, `add_key`, `remove_key`, `list_keys`). Export/import use `KeyManager` with no repository lock, manifest, or cache. `change-location` validates configurability, constructs a new same-class key with copied key material and optional AEAD session/cipher attributes, saves it to the new target using the existing passphrase/algorithm/label, updates manifest/repo object/cache key references, and optionally removes the old key file/blob. The parser includes mutually exclusive key selectors for export/remove and import options for paper/keyfile/repokey.

## State and Persistence Behavior

These commands mutate local key files, repository key blobs, manifest key references, and cache key references depending on mode. Passphrase changes re-encrypt key material but do not change repository encryption secrets. Add/remove manage independent Borg key wrappers around the same secret material. Export writes encrypted key backups, paper keys, or QR HTML to a path/stdout. Import reads key backups or interactive paper-key data and writes key storage. `change-location` moves or copies the active key between keyfile and repokey storage without changing crypto algorithms.

## Dependencies and Integration Points

The module integrates with crypto key classes via duck-typed capability methods, `KeyManager` backup/import formats, repository/manifest/cache wrappers, and parser choices derived from key location names. It is tied to `repo_create_cmd.py` because repository creation establishes the initial key and user-facing backup guidance.

## Risks and Edge Cases

Unencrypted repositories reject key operations that require key capabilities. `change-location` must preserve all cryptographic material exactly; missing attributes are conditionally copied for non-AEAD modes. Removing the wrong key can lock users out, so remove requires exactly one selector and underlying key logic protects admin/last keys. Export path validation handles directory paths specially. Paper import cannot use a path. Environment-dependent key locations (`BORG_KEY_FILE`, `BORG_KEYS_DIR`) affect import targets.

## Test Signals

Tests should cover encrypted, authenticated, and plaintext repositories; passphrase change capability errors; add/list/remove by label, key prefix, and current passphrase; admin/last-key protection; export normal, paper, and QR formats; import from file/stdin and paper mode errors; change-location keyfile-to-repokey and reverse with `--keep`; preservation of key IDs/labels/algorithm; and cache/manifest key references after movement.
