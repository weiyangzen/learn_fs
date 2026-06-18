# sources/sync-backup/bup/lib/bup/cmd/xstat.py

## Purpose
`xstat.py` prints detailed bup metadata for filesystem paths, with selectable metadata fields and timestamp resolution reduction.

## APIs and Control Flow
`parse_timestamp_arg` converts resolution tokens through `parse_timestamp`, requires the result to be 1 or a power of 10, and reports fatal parse errors. `main(argv)` parses include/exclude field flags in order, establishes the active metadata field set, sets `metadata.verbose`, then for each path calls `metadata.from_path(path, archive_path=path)`, rounds atime/mtime/ctime down when requested, and writes `metadata.detailed_bytes`.

## State, Dependencies, Integration, Risks, Tests
It is read-only except for stdout. Dependencies include `metadata.all_fields`, `metadata.from_path`, `metadata.detailed_bytes`, byte argv, and `parse_timestamp`. Risks include field order semantics, float division from `/` when rounding timestamps if values are ints, skipping ENOENT through `add_error`, and path metadata errors for special files. Test signals include resolution validation, include-before-exclude behavior, unknown fields, missing path handling, verbose/quiet effect, and formatting for multiple paths with blank separators.
