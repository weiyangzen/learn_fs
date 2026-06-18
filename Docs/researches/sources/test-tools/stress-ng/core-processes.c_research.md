# sources/test-tools/stress-ng/core-processes.c

Purpose: dumps currently running stress-ng-related processes on Linux for diagnostics.

Important APIs/functions: `stress_processes_dump`, with internal Linux-only `stress_processes_dump_filter`.

Control flow: Linux implementation scans `/proc` for numeric entries, computes PID column width, reads each process `cmdline`, filters to commands containing `stress-ng`, reads owner and status for parent PID/state, then logs a compact process line. Non-Linux builds provide an empty function.

State/persistence: no persistent state. It allocates a scandir list, reads procfs, resolves usernames unless statically built, and logs output.

Dependencies/integration: procfs, `scandir`, `alphasort`, filesystem read helpers, logging, `getpwuid`, and shim functions.

Risks: proc entries can disappear while being read; substring filtering may match helper commands; static buffers truncate long cmdlines; `getpwuid` may be unavailable in static builds.

Test signals: Linux diagnostic runs with multiple stress-ng children, disappearing-process races, static build ownership output, non-Linux no-op build, and long command-line handling.
