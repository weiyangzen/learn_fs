# sources/sync-backup/borg/docs/usage/key_add.rst.inc

Purpose: generated reference for `borg key add`, which adds another Borg key/passphrase wrapper to a repository.

Important APIs and control flow: command-specific option is `--label LABEL`, which must be unique. The command creates an additional Borg key containing the same secret key material as existing keys, protected by an independent passphrase read from `BORG_NEW_PASSPHRASE` or interactively.

State and persistence: mutates repository key metadata by adding a new labeled key. It does not re-encrypt repository data and does not alter existing keys.

Dependencies and integration points: repository encryption/key management, passphrase prompting/env handling, key labels, admin key protections, and future key deletion/unlock flows.

Risks: label collisions must be rejected. The initial `admin` label is reserved and protected from deletion. New key compromise exposes the same repository data because secret key material is shared.

Test signals: adding a key with a unique label, rejecting duplicate/reserved labels, unlocking repository with either old or new passphrase, ensuring no data rewrite occurs, and non-interactive `BORG_NEW_PASSPHRASE` handling.
