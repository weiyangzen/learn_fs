# File Research: sources/os/plan9/plan9/sys/src/cmd/time.c

Plan 9 `time` command.

Key responsibilities:
- Forks and execs the requested command, falling back to `/bin/<cmd>` for relative simple names.
- Waits for the child, retrying wait on interrupt notes.
- Prints user, system, and real time from `Waitmsg->time[]`.
- Echoes up to the first few command arguments in the timing line.
- Includes child exit status text when present.
- Ignores interrupt notes in the parent through `notifyf()`.

Notable behavior:
- Output is written to stderr.
- The parent exits with the child's wait message.
