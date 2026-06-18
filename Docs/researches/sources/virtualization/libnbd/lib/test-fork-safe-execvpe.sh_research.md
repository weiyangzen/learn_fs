# File Research: sources/virtualization/libnbd/lib/test-fork-safe-execvpe.sh

Comprehensive shell test for the custom fork-safe execvpe implementation.

Setup:
- Sources shared test functions.
- Requires `realpath`.
- Skips Darwin due to known killed-process behavior.
- Resolves helper binary path, including BusyBox workaround.

Test harness:
- `run0` invokes helper with PATH unset or set narrowly and captures command, stdout, stderr, and status.
- `run` uses same string for `program-to-exec` and argv0.
- `init_fail`, `execve_fail`, and `success` validate expected behavior.

Scenarios:
- Empty program name fails during init with `ENOENT`.
- Direct path candidates: empty dir, FIFO, directory, non-executable file, trailing slash, symlink loop.
- Binary executable success via copied `expr`.
- ENOEXEC fallback to `/bin/sh` for executable script without shebang.
- PATH unset fallback to `confstr(_CS_PATH)`.
- Explicit PATH lists preserve candidate order and nonfatal execve retry behavior.
- Empty PATH elements expand to current directory.

Interactions:
- Validates the detailed semantics implemented in `utils.c`.

Research notes:
- The script encodes POSIX PATH behavior and ENOEXEC shell fallback expectations very explicitly.
