# File Research: sources/os/plan9/plan9/sys/src/cmd/mkdir.c

Implements Plan 9 `mkdir`.

Behavior:
- Usage: `mkdir [-p] [-m mode] dir...`.
- Default mode is `0777`.
- `-m` parses octal mode and rejects values above `0777`.
- `-p` creates missing path components.

Key functions:
- `makedir()` checks existence, creates with `DMDIR | mode`, and records error state.
- `mkdirp()` walks slash-separated path prefixes and creates missing directories.
- `main()` parses flags and applies selected behavior.

Notes:
- Without `-p`, existing paths are reported as errors.
- Exit status is `"error"` if any create failed.
