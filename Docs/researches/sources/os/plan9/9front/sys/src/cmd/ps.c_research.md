# File Research: sources/os/plan9/9front/sys/src/cmd/ps.c

Plan 9 process status command. It reads `/proc`, sorts process directories numerically, reads each `status` file, and prints user, pid, optional note id/runtime/priority fields, CPU times, memory, state, and command or full args.

Key behavior:
- Options: `-a` full args, `-p` priorities, `-n` note id, `-r` real runtime.
- `ps` reads `/proc/<pid>/status` and optionally `/proc/<pid>/noteid` and `/proc/<pid>/args`.
- `cmp` sorts by numeric process id.

Integration points:
- Depends on Plan 9 `/proc` file formats and `tokenize`.
- Uses `Biobuf` for stdout.

Risks:
- Status parsing assumes at least 12 tokens and exact field positions.
- Reads args into a fixed 256-byte buffer and truncates long command lines.
