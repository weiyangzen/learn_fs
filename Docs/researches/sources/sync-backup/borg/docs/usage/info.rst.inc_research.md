# sources/sync-backup/borg/docs/usage/info.rst.inc

Purpose: generated reference for `borg info`, which displays detailed archive information.

Important APIs and control flow: accepts optional archive `NAME`, `--json`, and archive filters. It can target a single archive or filtered archive set depending on command implementation and filter use.

State and persistence: read-only metadata query. It reads repository/archive metadata and emits human or JSON output.

Dependencies and integration points: archive specification and matching, stats accounting, JSON output, common repository options, and deduplication/chunk index concepts.

Risks: deduplicated size for an individual archive means chunks unique to that archive, while all-archives deduplicated size means all chunks in the repository; adding per-archive numbers is wrong.

Test signals: human and JSON output schema, duplicate archive names with `aid:` selection, filtered archive info, and size accounting fixtures with shared chunks.
