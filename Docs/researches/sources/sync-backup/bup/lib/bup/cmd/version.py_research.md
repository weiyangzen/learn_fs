# sources/sync-backup/bup/lib/bup/cmd/version.py

## Purpose
`version.py` prints the bup version, build/source date, or commit ID.

## APIs and Control Flow
The module defines `version_rx`, a regex for acceptable version strings, though this file does not use it directly. `main(argv)` rejects positional arguments, allows at most one of `--date` and `--commit`, wraps stdout as bytes, and writes `version.date` truncated at the first space, `version.commit`, or `version.version`.

## State, Dependencies, Integration, Risks, Tests
It is read-only and depends on generated `bup.version` values plus byte-stream output. It is used by support diagnostics and remote command allowlists. Risks are minimal: unused `version_rx` can drift, `date.split` assumes byte date format, and option booleans are summed numerically. Test signals include no-arg version output, date and commit modes, mutual exclusion, unexpected arg fatal, and byte newline formatting.
