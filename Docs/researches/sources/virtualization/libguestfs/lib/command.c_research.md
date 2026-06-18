# File Research: sources/virtualization/libguestfs/lib/command.c

## Role
Implements the host-side internal subprocess runner used throughout libguestfs for qemu-img, supermin, tar, cp, and other external tools.

## Command Construction
- Supports execv-style argument vectors and system-style shell command strings.
- Provides quoted and unquoted shell-string append helpers.
- Supports formatted argument addition.
- Enforces one command style per command object.

## Execution Model
- `guestfs_int_cmd_run()` finalizes, logs, forks, captures output, loops over file descriptors, and waits.
- Child process resets signal handlers, closes extra file descriptors, sets umask `022`, runs optional child setup, applies optional rlimits, sets `LC_ALL=C`, and then `execvp()`s or runs `system()`.
- Stdout callbacks can be line-buffered, unbuffered, or whole-buffer.
- Stderr can be captured into appliance event callbacks or redirected to stdout.

## Pipe Mode
- `guestfs_int_cmd_pipe_run()` is a popen-like interface for streaming stdin/stdout to a child.
- It stores child stderr in a temporary file retrievable with `guestfs_int_cmd_get_pipe_errors()`.
- `guestfs_int_cmd_pipe_wait()` waits for the child.

## Cleanup
`guestfs_int_cmd_close()` frees arguments, temp error files, buffers, child rlimit records, open fds, and waits for any still-running child without reporting errors.

## Filesystem/Storage Relevance
This is the core command execution layer for host-side image creation, appliance building, archive transfer helpers, firmware copying, and external storage tooling.
