# File Research: sources/os/bsd/netbsd-src/lib/libwrap/options.c

## Summary
Implements TCP wrappers `hosts_options(5)` option parsing and execution. It parses colon-separated access-control options, validates option arguments, performs percent expansion where required, and dispatches side-effecting handlers such as UID/GID changes, socket options, shell commands, banners, `allow`, and `deny`.

## Main Responsibilities
- Parse option fields with escaped `\:` handling and optional `=` separators.
- Enforce option metadata: required argument, optional argument, no argument, must-be-last, and percent-expanded argument.
- Execute access decisions through `longjmp(tcpd_buf, AC_PERMIT/AC_DENY)`.
- Implement runtime options: `user`, `group`, `umask`, `linger`, `keepalive`, `spawn`, `twist`, `rfc931`, `setenv`, `nice`, `severity`, `allow`, `deny`, and `banners`.
- Support dry-run verification mode for `tcpdmatch`-style callers.

## Key Interfaces
- `process_options(char *options, struct request_info *request)`: top-level parser/dispatcher.
- Global `dry_run`: suppresses irreversible side effects during verification.
- Option handlers call shared libwrap helpers including `percent_x()`, `shell_cmd()`, `eval_*()`, `clean_exit()`, `tcpd_warn()`, and `tcpd_jump()`.

## Risks
This file intentionally performs irreversible side effects in ACL processing. Error handling uses non-local jumps, so adding options requires care around cleanup and ordering. `twist` replaces the process with `/bin/sh -c`, `spawn` executes shell commands, `setenv` mutates process environment, and `user`/`group` change process credentials. `get_field()` mutates the input string and stores parsing state statically, so it is not reentrant.
