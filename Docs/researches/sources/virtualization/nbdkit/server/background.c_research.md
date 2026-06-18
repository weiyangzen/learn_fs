# File Research: sources/virtualization/nbdkit/server/background.c

Implements daemonization for nbdkit.

Key behavior:
- Global `forked_into_background` records whether daemonization occurred, used by logging.
- On non-Windows:
  - `fork_into_background` returns immediately when `foreground` is set.
  - Otherwise it forks; parent exits success.
  - Child changes directory to `/`.
  - If not verbose, stderr is redirected to stdout, which should already point at `/dev/null`.
  - Sets `forked_into_background=true` and logs the new pid.
- `chdir_root` is separate to support older GCC diagnostic pragmas around ignored `chdir` result.
- On Windows:
  - Daemonizing is unsupported; without foreground mode it prints an error and calls `NOT_IMPLEMENTED_ON_WINDOWS`.

Dependencies:
- `internal.h` globals `foreground`, `verbose`, debug helper, and Windows not-implemented macro.
- POSIX `fork`, `chdir`, `dup2`.

Notes:
- This file only backgrounds the process; earlier setup is responsible for stdin/stdout redirection.
