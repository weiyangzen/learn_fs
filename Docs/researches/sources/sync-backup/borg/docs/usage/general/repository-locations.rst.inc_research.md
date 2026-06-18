# sources/sync-backup/borg/docs/usage/general/repository-locations.rst.inc

Purpose: documents how commands receive repository locations and archive names.

Important APIs and control flow: repository location comes from `-r/--repo` or `BORG_REPO`. Commands needing one or two archive names take them as positionals; commands operating over many archives usually accept `-a`.

State and persistence: no direct state; repository selection determines all subsequent repository reads/writes.

Dependencies and integration points: common `--repo`, environment configuration, archive filters, `borg mount` directory naming, and shell quoting.

Risks: archive names cannot contain `/` and should avoid shell- or filesystem-special characters. Ambiguous or awkward names complicate mount paths and scripts.

Test signals: repository env fallback, explicit repo override, archive-name validation, and command-specific positional/archive-filter parsing.
