# sources/user-network-fs/nfs-ganesha/src/valgrind.sh

Purpose: `valgrind.sh` is a tiny wrapper to run an arbitrary command under Valgrind leak checking with a larger permitted stack frame and a fixed log file.

Important behavior: it invokes `valgrind --leak-check=full --max-stackframe=3280592 --log-file=/tmp/valgrind.log $*`.

Control flow: the script has a single command and passes all arguments to Valgrind. There is no option parsing or cleanup.

State and persistence: it writes Valgrind output to `/tmp/valgrind.log`, overwriting or appending according to Valgrind behavior. It does not create per-run logs.

Dependencies and integration points: depends on `/bin/sh` and Valgrind. It is likely used manually for Ganesha binaries that exceed Valgrind's default stack-frame expectations.

Risks: unquoted `$*` performs shell word splitting and glob expansion, so arguments containing spaces are unsafe. The fixed `/tmp/valgrind.log` path causes concurrent runs to collide. Exit status is Valgrind's status; the script does not post-process failures.

Test signals: invoke with a command containing spaces or options to confirm argument handling, and run concurrent invocations to validate log collision expectations.
