<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioprio.c -->
# sources/test-tools/strace/tests/ioprio.c

Purpose: Tests decoding of `ioprio_get` and `ioprio_set`, including process and process-group selectors, priority class/value formatting, invalid selectors, and optional PID namespace translation.

Important APIs/types/functions: Uses `syscall(__NR_ioprio_get)`, `syscall(__NR_ioprio_set)`, `getpid`, `getpgid`, `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`, and xlat table `ioprio_class`.

Control flow: The program prints a bogus `ioprio_get`, a real process `ioprio_get`, an `ioprio_set` for the current process group with `IOPRIO_CLASS_NONE`, and a bogus `ioprio_set` with a malformed priority. Output branches on `XLAT_RAW`, `XLAT_VERBOSE`, and abbreviated mode.

State/persistence behavior: It may attempt to set the process group's I/O priority, but the chosen class/value and permission context are test-local. PID namespace mode only affects printed pid annotations.

Dependencies: Requires both ioprio syscalls, pid namespace helper support, and the ioprio xlat table.

Integration points: Validates strace syscall decoders, xlat verbosity modes, priority bit packing via `IOPRIO_PRIO_VALUE`, and pid namespace translation rendering.

Risks: Kernel permission rules or cgroup/scheduler behavior can alter return codes. Namespace annotations differ when compiled through the PIDNS wrapper.

Test signals: Expected lines include unknown selector fallback, current PID/PGID annotations, optional decoded return priority, and final `+++ exited with 0 +++` with pidns leader prefix.

Source read signal: complete file read for this research pass; file size 134 line(s), 3312 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioprio.c -->
