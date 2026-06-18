# sources/sync-backup/rsync/.github/workflows/valgrind.yml

Purpose: memory-error CI using Valgrind.

Important APIs/types/functions: configures with `--enable-debug`, builds `check-progs`, runs `runtests.py --valgrind` across a matrix of privilege/transport, preserves scratch, scans `valgrind.*.log` for nonzero error summaries, and uploads logs on failure.

Control flow: suite is allowed to finish even if individual tests fail; the explicit log scan is the gate. Leak checking is disabled because rsync intentionally leaves process-exit allocations.

State and persistence: failure artifact `valgrind-logs-<privilege>-<transport>` retained 7 days.

Dependencies/integration: depends on Valgrind, suppression file, sudo for root matrix, and testtmp log layout.

Risks: missing logs fail the job; suppression drift or Valgrind version changes can add noise.

Test signals: unsuppressed invalid reads/writes, uninitialized uses, bad frees, and syscall parameter issues fail the workflow.
