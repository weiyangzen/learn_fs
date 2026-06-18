# File Research: sources/os/plan9/9front/sys/src/cmd/lock.c

`lock` opens a Plan 9 exclusive-use lock file and keeps the lock alive while running a command, defaulting to `rc`.

It ensures the file has `DMEXCL` set, reopens it so exclusive locking takes effect, forks a keeper process that periodically writes to the lock fd, then runs the command in a separate process group/environment. When the command exits, it kills the keeper and exits with the command’s wait status.

Options:
- `-w` waits/retries opening the lock.
- `-d` sets a debug flag, though the flag is not materially used.

It is Plan 9 lock-file orchestration around exclusive files and process notes.
