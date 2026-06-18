# File Research: sources/os/plan9/plan9/sys/src/cmd/init.c

`init.c` is the Plan 9 user-level init process.

Key behavior:
- Closes leftover boot fds, sets priority, initializes environment (`objtype`, `service`, `timezone`), creates a new namespace, and determines CPU vs terminal service.
- On CPU service without manual mode, runs `/rc/bin/cpurc` once.
- Then repeatedly starts `/bin/rc`, with terminal service using `termrc` and profile setup.
- `fexec` forks child exec functions and waits, handling notes and fatal exec failures.
- `pass` prompts for and verifies a DES-key password from a key fd, though it is not used by `main` in this file.
- `readenv`, `setenv`, and `cpenv` operate directly on Plan 9 environment files.

Important dependencies:
- Uses Plan 9 `/dev`, `#e`, `#c`, authsrv DES key helpers, and namespace setup.

Notable risks/quirks:
- `setenv` calls `fprint(fd, val)` directly, so values are treated as format strings.
- The process intentionally loops forever restarting shell sessions.
