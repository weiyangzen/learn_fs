# sources/sync-backup/borg/docs/usage/extract.rst.inc

Purpose: generated reference for `borg extract`, which restores files from an archive.

Important APIs and control flow: accepts archive `NAME`, optional pattern-capable paths, list/dry-run, numeric IDs, metadata toggles, stdout, sparse output, continue mode, include/exclude patterns, and strip-components. Default path interpretation is literal path prefix (`pp:`).

State and persistence: writes restored filesystem objects into the current working directory unless `--stdout` or `--dry-run` is used. `--continue` resumes an interrupted extraction of the same archive.

Dependencies and integration points: archive item reader, decrypt/decompress/hash verification, metadata restoration, pattern engine, sparse file handling, and filesystem permissions.

Risks: extraction always targets `.` so wrong working directory can restore into unintended locations. If parent directories are not extracted, parent metadata cannot be restored. `--progress` adds an extra metadata pass.

Test signals: dry-run hash/decrypt/decompress without writes, stdout mode, metadata toggles, sparse output, interrupted continue, strip-components skipping, and selected path pattern behavior.
