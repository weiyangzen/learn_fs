# File Research: sources/os/plan9/9front/sys/src/cmd/snap/snap.c

Purpose: CLI entry point for taking process snapshots.

Behavior:
- Usage: `snap [-d] [-o snapfile] pid...`.
- Opens output, writes a snapshot header containing time, user, system, architecture, kernel root mtime, and terminal.
- Skips snapshotting its own pid.
- Calls `snap(pid, 1)` for each requested process and serializes with `writesnap`.

Integration: Uses `take.c` for capture, `write.c` for serialization, and `util.c` allocation helpers.

Risks:
- Requires readable `/proc/<pid>` files.
- Snapshot output defaults to stdout.
