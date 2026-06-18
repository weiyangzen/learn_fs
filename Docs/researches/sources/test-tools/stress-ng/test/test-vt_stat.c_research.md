<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vt_stat.c -->
# sources/test-tools/stress-ng/test/test-vt_stat.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux virtual-terminal type `struct vt_stat``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/vt.h`, declares the relevant object or arguments, and then declares `struct vt_stat`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the probe depends on Linux console UAPI headers. It does not open a tty or issue ioctls, so it cannot validate runtime VT permissions or actual console availability.

Test signals: compile success confirms `struct vt_stat` exists for VT ioctl stressor code; missing headers/types should gate that code out.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vt_stat.c -->
