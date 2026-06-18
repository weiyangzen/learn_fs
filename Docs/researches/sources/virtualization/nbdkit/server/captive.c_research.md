# File Research: sources/virtualization/nbdkit/server/captive.c

Implements the `--run` captive mode, where nbdkit runs as a child while an external command runs as the parent/client command.

Key behavior:
- On non-Windows, `run_command` returns if no `run` command was configured.
- Builds an in-memory shell script assigning:
  - `uri`
  - `nbd` as a synonym for `uri`
  - `exportname`
  - `port`
  - `unixsocket`
  - TLS variables `tls`, `tls_certificates`, `tls_psk`
- Values are shell-quoted with `shell_quote`; the configured run command is appended unquoted by design.
- Forks:
  - Parent restores saved stdin/stdout, executes the command with `system`, maps its exit/signal status, then checks the nbdkit child.
  - If child is still running, parent sends `SIGTERM` and waits so plugin cleanup runs.
  - If child exited unexpectedly and the external command succeeded, child status becomes the result.
  - Parent exits with the selected status.
  - Child frees the generated command and continues running nbdkit, logging a background-fork debug message.
- On Windows, `--run` is unsupported.

Dependencies:
- `open_memstream` compatibility wrapper.
- `shell_quote` utility.
- `internal.h` globals for run command, URI/export/socket/TLS values, saved stdin/stdout, program name, and debug/error helpers.

Notes:
- The external command is intentionally executed via the shell so variable assignments and complex command strings work.
- Captive nbdkit cleanup is best-effort through SIGTERM and wait; the external command’s exit code normally takes precedence.
