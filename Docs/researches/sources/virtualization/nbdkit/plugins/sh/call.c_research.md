# File Research: sources/virtualization/nbdkit/plugins/sh/call.c

Implements the generic shell-script invocation layer used by the `sh` subplugin. `call3` creates stdin/stdout/stderr pipes, forks, installs the script environment with `$tmpdir`, executes the script method, concurrently writes stdin and reads stdout/stderr with `poll`, handles missing-shebang fallback on non-glibc systems, restores child SIGPIPE defaults, waits for completion, and returns the raw script exit code.

`handle_script_error` normalizes script exit codes into nbdkit behavior. It maps OK, method-missing, false, shutdown, and disconnect codes; parses recognized errno names at the start of stderr; trims and logs stderr; calls `nbdkit_shutdown`/`nbdkit_disconnect` for special statuses; and sets `errno` for nbdkit's preserved-errno paths.

Public wrappers `call`, `call_read`, and `call_write` expose no-stdout, stdout-returning, and stdin-writing variants for method dispatch. The implementation is careful about CLOEXEC when available, avoids deadlock by polling all pipes, and deliberately ignores `EPIPE` on script stdin so scripts may exit early after deciding an error.
