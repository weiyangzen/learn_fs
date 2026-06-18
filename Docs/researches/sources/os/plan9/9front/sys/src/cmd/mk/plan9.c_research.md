# File Research: sources/os/plan9/9front/sys/src/cmd/mk/plan9.c

Provides Plan 9 OS integration for mk: environment import/export, process execution, waiting, notes, file timestamp cache, and shell setup.

Key behavior:
- Uses `/bin/rc` and shell name `rc`.
- `readenv()` copies `/env` into mk variables while excluding invalid shell names and internal variables.
- `exportenv()` writes selected variables back into a copied `/env`.
- `pipecmd()` runs commands under rc with optional stdout pipe and exported environment.
- `execsh()` optionally captures command output into a buffer.
- Handles waits, process termination notes, interrupt/hangup cleanup, file touch via `dirwstat`, and directory bulk mtime caching.

Important dependencies: Plan 9 rfork/env model, `/env`, `Waitmsg`, `Dir`, rc shell, `dirread`, `dirstat`.

Notable risks:
- Environment export mutates child `/env` files, not POSIX-style env arrays.
- Directory mtime caching depends on `S_BULKED` and can serve cached values unless forced.
