# File Research: sources/virtualization/nbdkit/server/password.c

Purpose: Implements exported password-reading helper `nbdkit_read_password`.

Accepted forms:
- `"-"` reads interactively from a tty using `readpassphrase`.
- `"-FD"` reads from an already-open numeric file descriptor, excluding stdin/stdout/stderr.
- `"+PATH"` opens and reads a password from a file.
- Any other value is treated as the literal password.

Interactive behavior:
- Refuses interactive reads when `nbdkit_stdio_safe()` is false, such as after config phase or with stdin serving.
- Requires a tty via `RPP_REQUIRE_TTY`.
- Copies the password to heap memory and clears the stack buffer with `explicit_bzero` when available.

File descriptor/file behavior:
- `read_password_from_fd` wraps the fd with `fdopen`, reads one line with `getline`, closes the stream, and strips a trailing newline.
- EOF without data becomes an empty password.
- The helper owns and closes the fd it reads from.

Platform behavior:
- Reading from numeric file descriptors is disabled on Windows.
- Errors are reported with `nbdkit_error`.
