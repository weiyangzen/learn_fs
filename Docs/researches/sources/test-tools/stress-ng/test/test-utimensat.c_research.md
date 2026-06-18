<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-utimensat.c -->
# sources/test-tools/stress-ng/test/test-utimensat.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``utimensat(2)``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `string.h`, `fcntl.h`, and `sys/stat.h` with `_GNU_SOURCE`, declares the relevant object or arguments, and then zeroes a two-element `timespec` array and calls `utimensat(0, "/tmp", times, 0)`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: runtime execution may try to change `/tmp` timestamps and normally requires ownership/permissions. The first argument is `0` rather than `AT_FDCWD`, but the absolute path makes the descriptor irrelevant.

Test signals: compile success proves the prototype and `struct timespec` are available; runtime status shows whether the libc/kernel pair accepts the call.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-utimensat.c -->
