# sources/storage-engines/wiredtiger/tools/antithesis/test.sh

## Purpose
`test.sh` is the container entrypoint wrapper for running WiredTiger `test/format` inside the Antithesis image. It sets runtime library paths, starts the workload, and prints a bounded GDB backtrace if the workload leaves a core after failure.

## Important commands and variables
The script exports `LD_LIBRARY_PATH=/opt/bin:/opt/tools/voidstar/lib:$LD_LIBRARY_PATH`, changes to `./bin/test/format`, runs `./t "$@" 2>&1 &`, waits for the child PID, stores the return code, and on nonzero status invokes `gdb --batch` with `thread apply all backtrace 30` against `t *core*`.

## Control flow and behavior
The workload runs in the background so the script can capture and wait on its PID. The exit status is propagated after optional debugging output. All arguments passed to the script are forwarded to `./t`.

## State, dependencies, and integration
The script depends on the container filesystem layout, dynamic libraries in `/opt/bin` and `/opt/tools/voidstar/lib`, GDB, and the `test/format` executable `t`. It integrates with `docker-compose.yaml`, which calls it with `CONFIG.antithesis` and workload flags.

## Risks and test signals
The shebang is `/bin/sh` but the script uses `[[ ... ]]`, which requires a shell that supports Bash/Ksh syntax; this is a portability risk unless `/bin/sh` is Bash-compatible in the image. `gdb t *core*` is also glob-dependent and may fail or choose unexpectedly with zero/multiple cores. Signals are test stdout/stderr, preserved exit code, and GDB backtraces on nonzero failures.
