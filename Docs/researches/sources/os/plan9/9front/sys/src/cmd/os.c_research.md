# File Research: sources/os/plan9/9front/sys/src/cmd/os.c

## Role

Runs a command through a remote command service mounted at `/mnt/term/cmd`.

## Main Behavior

The program opens the remote `clone` control file, reads the per-command directory name, opens `wait`, and optionally opens foreground `data` and `stderr` streams. It can set remote directory and nice level, enables `killonclose` for foreground jobs, and writes an `exec` command with quoted arguments.

Foreground mode forks copy processes for stdin, stdout, and stderr, plus a wait-reader process. Background mode skips the data stream copying.

## Options

Supports selecting mount point, explicit remote directory, background mode, and nice value. If no directory is given, it tries to translate the current directory relative to `/mnt/term` or `/mnt/term/root`.

## Process Handling

Interrupt, hangup, and kill notes are caught and translated to a remote `kill` control write. Local copy processes are tracked so the stdin copier can be killed at exit.
