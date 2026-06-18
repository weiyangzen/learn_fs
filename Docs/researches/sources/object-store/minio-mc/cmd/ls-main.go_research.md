# Research: sources/object-store/minio-mc/cmd/ls-main.go

Purpose: implements top-level `mc ls` command argument parsing and dispatch.

Important APIs/types/functions: `lsFlags`, `lsCmd`, `rewindSupportedFormat`, `parseRewindFlag`, `checkListSyntax`, and `mainList`.

Control flow: `parseRewindFlag` parses fixed date formats or positive durations into a reference time. `checkListSyntax` defaults to `.`, rejects blank args, parses recursive/incomplete/version/summary/storage-class/zip options, and rejects zip with versions/rewind. `mainList` configures colors, initializes clients for each target, stats non-slash targets to append a separator for directories, and calls `doList`.

State and persistence: read-only listing. No persistence.

Dependencies/integration points: shared client abstraction, duration parser, global context, and `doList` from `ls.go`. `parseRewindFlag` is reused by legalhold commands.

Risks: local timezone affects rewind date interpretation. Zip listing is limited to latest version. Directory stat before listing adds extra remote/local calls.

Test signals: no direct tests here; useful tests cover rewind formats, invalid negative duration, zip conflicts, default target, and directory separator adjustment.
