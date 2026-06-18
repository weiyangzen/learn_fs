# File Research: sources/os/bsd/netbsd-src/lib/libwrap/shell_cmd.c

## Summary
Executes a shell command for TCP wrappers `spawn` options. The command runs in a child process through `/bin/sh -c`, with standard descriptors redirected to `/dev/null`.

## Main Responsibilities
- Fork a child and wait for that specific child in the parent.
- In the child, ignore `SIGHUP`, close descriptors 0-2, open `/dev/null`, duplicate it to stdin/stdout/stderr, and exec the shell.
- Log fork, open, dup, or exec failures.

## Key Interfaces
- `shell_cmd(char *command)`.

## Risks
The command is shell-executed, so safety depends on prior argument construction and `percent_x()` sanitization. The parent waits with `wait()` rather than `waitpid()`, consuming unrelated exited children until the target child appears.
