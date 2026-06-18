<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ustat.c -->
# sources/test-tools/stress-ng/test/test-ustat.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `the obsolete `ustat(2)` interface`. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `sys/types.h`, `unistd.h`, `ustat.h`, and Linux `sys/sysmacros.h` for `makedev()`, declares the relevant object or arguments, and then builds a block-device `dev_t`, declares `struct ustat`, and calls `ustat(dev, &ubuf)`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the file deliberately errors out on GNU Hurd and aarch64 because the interface is absent or always fails there. On modern libc/kernel combinations `ustat` may be deprecated, hidden, or link-compatible but unusable at runtime.

Test signals: compile success proves the header, `struct ustat`, `makedev`, and symbol are visible; compile failure or the explicit `#error` disables dependent stress-ng code. Runtime failure is expected on many systems and should not be read as persistent state damage.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ustat.c -->
