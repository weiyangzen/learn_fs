<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/sfd.c -->
# sources/test-tools/strace/attic/test/sfd.c

Purpose: helper for reading signal-related bitmaps from `/proc/<pid>/stat`.

Important logic: parses a target pid from `argv[1]`, opens `/proc/<pid>/stat`, reads into a fixed buffer, advances across 30 space-delimited fields, then `sscanf`s four integers named `signal`, `blocked`, `ignore`, and `caught` and prints them as hex.

Control flow: straight-line file read and manual field scanning.

State and persistence: read-only access to procfs; no persistent state.

Dependencies and integration: depends on Linux procfs stat field layout as it existed when written.

Risks: no argument validation; command names in `/proc/<pid>/stat` can contain spaces within parentheses, making naive space counting fragile. Integers may be too small for modern signal masks. Test signals: compare output against `/proc/<pid>/status` signal masks on a known process.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/sfd.c -->
