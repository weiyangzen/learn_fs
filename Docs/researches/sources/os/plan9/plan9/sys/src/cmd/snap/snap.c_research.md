# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/snap.c

CLI entry point for taking process snapshots.

Key behavior:
- Usage: `snap [-o snapfile] pid...`.
- Writes to stdout by default or `-o` output path.
- Emits a snapshot header with time, user, system, architecture, kernel root mtime, and terminal.
- Skips snapshotting itself.
- Calls `snap(pid, 1)` and `writesnap()` for each target process.

Important details:
- Uses `dirstat("#/")` to record kernel compilation/root metadata.
- Defaults unknown user/system/arch/terminal fields to placeholder strings.

Filesystem relevance:
- Direct: writes snapshot files and starts capture from Plan 9 `/proc`.
