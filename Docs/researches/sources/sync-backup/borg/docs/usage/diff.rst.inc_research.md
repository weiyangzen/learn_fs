# sources/sync-backup/borg/docs/usage/diff.rst.inc

Purpose: generated reference for `borg diff`, which compares two archives' file content and metadata.

Important APIs and control flow: accepts `ARCHIVE1`, `ARCHIVE2`, optional pattern-capable paths, metadata/content options, `--same-chunker-params`, custom `--format`, JSON Lines, sorting, and `--content-only`. It compares matching items, uses chunk IDs when chunker parameters match, otherwise compares content, and reports added/removed/modified paths plus metadata changes.

State and persistence: read-only repository/archive operation. It may load metadata and chunks but does not write archive state.

Dependencies and integration points: pattern matching, archive item metadata, chunker parameters, Python format-string syntax, JSON Lines output, and sorting fields.

Risks: `--same-chunker-params` can force unsafe assumptions if archives are not comparable. Custom format keys are a user-facing contract. Content comparison can be much slower when chunker parameters differ.

Test signals: fixtures for added/removed/modified files, metadata-only changes, content-only suppression, JSON Lines schema, format variables, and stable multi-field sorting.
