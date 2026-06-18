# sources/sync-backup/borg/docs/usage/key_remove.rst.inc

Purpose: Documents `borg key remove`, which removes one repository key selected by label, id/prefix, or current passphrase-unlocked key.

Important APIs/types/functions: CLI contract is `borg [common options] key remove [options]`. Mutually exclusive selectors are `--label LABEL`, `--key ID`, and `--passphrase`.

Control flow: Documentation states exactly-one selector semantics. Runtime should validate one selector, resolve the key, reject protected cases, remove key metadata/storage, and leave the repository usable through remaining keys.

State and persistence: Mutates repository key set. The `admin` key and last remaining key are protected from removal, preventing complete lockout through this command.

Dependencies and integration points: Integrates with `key list` for IDs/prefixes, repository unlocking, key labels, and passphrase selection.

Risks: High destructive potential because removing a key can lock out a user. Parser validation and protected-key checks are critical. Unique-prefix handling must reject ambiguous prefixes.

Test signals: Tests should cover selector exclusivity, admin-key protection, last-key protection, ambiguous key prefix errors, label lookup, active-key removal, and subsequent unlock behavior.
