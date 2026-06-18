# File Research: sources/windows/dokany/dokan_fuse/src/fuse_helpers.c

Implements FUSE helper command-line parsing, daemonization, version reporting, signal handling, and Cygwin semaphore wrappers.

Key behavior:
- Parses helper options:
  - `-d`, `debug`, `-f`, `-s`, `fsname=`;
  - help/version keys;
  - first non-option as mountpoint.
- `fuse_parse_cmdline`:
  - runs option parsing;
  - adds default `-ofsname=<program basename>` if none supplied;
  - returns mountpoint, multithreaded flag, and foreground flag.
- `fuse_daemonize`:
  - on Cygwin, calls `daemon(0, 0)`;
  - elsewhere on Windows, detaches with `FreeConsole`.
- `fuse_version` returns `FUSE_VERSION`.
- Cygwin signal support stores a global session and exits it on HUP/INT/TERM, ignores PIPE, and restores defaults on removal.
- Non-Cygwin signal handlers are no-ops.
- Cygwin semaphore wrappers map POSIX-like calls to Windows semaphore handles.

Risks and notes:
- Mountpoint handling deliberately avoids `realpath` because Cygwin paths do not match Dokan’s expectations.
- Non-Cygwin “daemonize” can fail if `FreeConsole` fails.
