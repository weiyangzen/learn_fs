# sources/sync-backup/bup/dev/clear-bupm-entries

## Purpose
Developer utility to replace selected metadata entries in a `.bupm` stream with empty entries for corruption/edge-case testing.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-python`, uses `argparse`, `metadata._ArchiveIterator`, and `Metadata().write`.

## Control Flow
Parses zero-based indexes, iterates metadata records from stdin, writes empty metadata for requested indexes, writes original records otherwise, and errors if requested indexes were not present.

## State and Persistence Behavior
Transforms stdin to stdout; does not persist files itself. Output stream is a modified archive metadata stream.

## Dependencies and Integration Points
Depends on bup metadata encoding and the developer Python launcher.

## Risks and Test Signals
Risks are private `_ArchiveIterator` coupling and index mismatch. Signals are output stream decodability and exit 2 when requested entries do not exist.
