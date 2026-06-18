<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-process-vm-writev.c -->
# sources/test-tools/stress-ng/test/test-process-vm-writev.c

Purpose: minimal stress-ng configure probe for the cross-process writev API; it compiles and often lightly invokes `process-vm-writev`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/uio.h`; uses types `struct iovec`, `pid_t`; defines `main`; calls `process_vm_writev`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/uio.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-process-vm-writev.c -->
