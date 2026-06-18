# sources/sync-backup/bup/dev/checksum

## Purpose
Portable helper to compute a SHA1 or SHA256 digest from a path or stdin across GNU/Linux and BSD/macOS command naming.

## Important APIs, Types, and Functions
Shell options parse `-t sha1|sha256`, optional `--`, and optional single `PATH`. It chooses `sha1sum`/`sha256sum` when available or `sha1`/`sha256 -q` otherwise.

## Control Flow
Validates arguments, records the selected digest kind, runs the platform command with or without a source path, and strips GNU `*sum` filename suffixes by printing text before the first space.

## State and Persistence Behavior
No persistent state; reads stdin or one file.

## Dependencies and Integration Points
Used by tests/dev scripts needing platform-neutral checksums.

## Risks and Test Signals
Risks are unusual filename output formats, missing digest utilities, and stdin handling. Signals are exact hex digest and exit 2 on misuse or missing tools.
