<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_file.c -->
# sources/user-network-fs/samba/source3/lib/util_file.c

## Purpose
`util_file.c` asynchronously runs a command and reads its output into memory with a maximum-size guard.

## Important APIs, types, and functions
`struct file_ploadv_state` tracks event context, read subrequest, maximum size, process-output fd, and accumulated buffer. Public APIs are `file_ploadv_send` and `file_ploadv_recv`; callback `file_ploadv_readable` drains output.

## Control flow
Send starts the process with `sys_popenv`, installs cleanup to close it, waits for fd readability, reads chunks of 1024 bytes, reallocates a null-terminated talloc buffer, enforces overflow and max-size checks, and waits again until EOF. Receive returns Unix error codes or moves the buffer to the caller.

## State and persistence behavior
Runtime state includes the child process pipe and accumulated output buffer. Cleanup closes the process fd with `sys_pclose`. No file state is persisted.

## Dependencies and integration points
It depends on async socket readability helpers, `sys_popenv`, `sys_read`, `sys_pclose`, talloc, tevent, and Samba utility error conventions. It supports code that needs command output without blocking the event loop.

## Risks and edge cases
Large output can return `EMSGSIZE`; integer wrap is explicitly checked. EOF completes successfully even with an empty buffer. Cleanup must run on cancellation to avoid process/fd leaks.

## Test signals
Tests should cover command-start failure, normal small output, empty output, max-size breach, read errors, cancellation cleanup, and null terminator handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_file.c -->
