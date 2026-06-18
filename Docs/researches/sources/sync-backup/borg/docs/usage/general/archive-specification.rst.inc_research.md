# sources/sync-backup/borg/docs/usage/general/archive-specification.rst.inc

Purpose: general documentation for specifying a single archive by ID or by name.

Important APIs and control flow: describes `aid:` prefix matching on archive fingerprints, with enough hex digits to uniquely identify one archive, and name-based lookup for old-style unique archive names.

State and persistence: read-only reference material; it documents immutable archive IDs and mutable/user-chosen names.

Dependencies and integration points: used by commands accepting archive names, especially `info`, `list`, `extract`, `delete`, and quickstart examples. Cross-links to archive matching patterns.

Risks: ambiguous names are common when users intentionally create archive series with repeated names. Too-short ID prefixes must be rejected or disambiguated by runtime code.

Test signals: parser tests for `aid:` abbreviation uniqueness, duplicate-name handling, and cross-command consistency for archive spec resolution.
