# File Research: sources/os/plan9/plan9/sys/src/cmd/lock.c

Read fully: 170 lines, 2728 bytes. SHA-256 prefix: `5c4a83a46bb8c95d`.

This command keeps an exclusive lock file open while running a command. It ensures the named lock file has `DMEXCL`, opens it read/write, forks a keeper process that periodically writes to maintain activity, then runs the requested command or `rc` by default in a child with a custom prompt.

Options:
- `-d` increments debug flag, though it is not otherwise used.
- `-w` waits until the lock opens instead of failing immediately.

After the command exits, it posts a note to kill the keeper, waits for it, reports nonempty status, and exits with the command’s status.

Dependencies: Plan 9 exclusive files, `rfork`, environment file `/env/prompt`, notes, and wait messages.

Risk notes: lock acquisition uses file exclusivity and a keeper process rather than advisory locking. Interrupt notes are continued by `notifyf()`.
