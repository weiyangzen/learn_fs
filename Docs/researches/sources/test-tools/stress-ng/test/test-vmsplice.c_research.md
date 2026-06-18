<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vmsplice.c -->
# sources/test-tools/stress-ng/test/test-vmsplice.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``vmsplice(2)``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `fcntl.h` and `sys/uio.h` with `_GNU_SOURCE`, declares the relevant object or arguments, and then creates an empty `iovec` and calls `vmsplice(3, &iov, 1, 0)`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the file intentionally uses a dummy fd, so execution will normally fail with `EBADF`; the aim is prototype/link detection. The syscall is Linux-specific and may be blocked by seccomp.

Test signals: compile/link success confirms libc exposes `vmsplice`; runtime failure with a normal errno still validates callability.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vmsplice.c -->
