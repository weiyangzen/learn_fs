# File Research: sources/os/plan9/plan9/sys/src/cmd/ps.c

Purpose: Implements Plan 9 `ps` by reading `/proc`.

Key behavior:
- Options: `-a` show args, `-p` show base/current priority, `-r` show real elapsed time.
- Changes to `/proc`, reads all directory entries, sorts numerically by pid.
- For each process, reads `<pid>/status`, tokenizes fields, and prints user, pid, times, optional priority/real time, memory size, state, and command.
- With `-a`, reads `<pid>/args` and prints arguments with newlines replaced by spaces.

Dependencies and integration:
- Assumes Plan 9 `/proc/<pid>/status` field layout.
- Uses `dirreadall`, `Dir`, `Bio`, and Plan 9 libc.

Risks and notes:
- Ignores processes that disappear or cannot be read.
- Fixed buffers for status and args.
- Sorting uses `atoi` on directory names.
