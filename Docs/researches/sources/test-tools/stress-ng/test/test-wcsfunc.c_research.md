<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-wcsfunc.c -->
# sources/test-tools/stress-ng/test/test-wcsfunc.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `platform-specific wide-character function availability via `WCSFUNC``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes BSD or libbsd headers plus `wchar.h`, selected by OS macros, declares the relevant object or arguments, and then places the macro-expanded `WCSFUNC` symbol into a static function-pointer array and checks whether the first pointer is null. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: `WCSFUNC` must be supplied by the configure harness, so standalone compilation without that definition fails. Header paths differ across BSD, GNU/libbsd, and GNU/kFreeBSD, making this a portability-sensitive probe.

Test signals: successful compilation proves the requested wide-character function is declared in the selected header set; link/runtime confirms the symbol can be referenced.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-wcsfunc.c -->
