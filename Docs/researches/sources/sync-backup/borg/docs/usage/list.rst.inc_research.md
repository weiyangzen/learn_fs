# sources/sync-backup/borg/docs/usage/list.rst.inc

Purpose: Documents `borg list`, which lists the contents of a single archive, optionally filtered by archive paths/patterns and rendered with custom formats or JSON Lines.

Important APIs/types/functions: CLI contract is `borg [common options] list [options] NAME [PATH...]`. Important options are `--short`, `--format FORMAT`, `--json-lines`, `--depth N`, and include/exclude pattern sources. Format keys include file metadata, timestamps, hashes, archive id/name, path, hardlink and symlink extras, and separators such as `NL` and `NUL`.

Control flow: Documentation is generated from parser actions and a long epilog with format notes. Runtime flow is read-only: resolve archive `NAME`, apply path/pattern filters and depth limit, iterate archive items, compute requested metadata/hash fields as needed, and output either text or JSON Lines.

State and persistence: Does not mutate repository state. It reads archive metadata and may load chunks if requested format keys require content-derived checksums/fingerprints.

Dependencies and integration points: Shares pattern semantics with create/extract/recreate and format-string semantics with `repo-list`. JSON Lines output is useful for automation and test fixtures, including transfer upgrade data generation.

Risks: Custom format keys can cause extra I/O or content hashing costs. JSON can only represent text, so binary metadata must be encoded or omitted consistently. Pattern semantics are easy to misread because archive paths are relative.

Test signals: Docs regeneration, parser snapshot tests, archive listing tests for `--short`, `--depth`, include/exclude patterns, JSON Lines schema, and format keys including symlink/hardlink extras and hashes.
