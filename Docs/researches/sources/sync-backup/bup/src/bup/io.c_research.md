## sources/sync-backup/bup/src/bup/io.c

Purpose: minimal C diagnostic helpers for Bup native code.

Important APIs: `msg(FILE*, fmt, ...)` writes `bup: ` plus formatted output to a stream. `die(exit_status, fmt, ...)` writes the same prefix to stderr and exits. Both are annotated for printf format checking and exit with `BUP_EXIT_FAILURE` if output itself fails.

State and dependencies: no persistent state; depends on stdio, stdarg, stdlib, `bup.h`, and `bup/io.h`.

Risks and tests: because diagnostics exit if writing fails, callers cannot recover from broken stderr/stdout. It is used by launcher and compatibility code; tests observe its output prefixes indirectly in command failure scenarios.
