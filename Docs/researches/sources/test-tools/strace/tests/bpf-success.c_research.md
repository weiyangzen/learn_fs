<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-success.c -->
## sources/test-tools/strace/tests/bpf-success.c

Purpose: Injected-success variant of the table-driven BPF syscall decoder test.

Important APIs/types/functions: Defines `INJECT_RETVAL 42` and includes `bpf.c`.

Control flow: The included `sys_bpf` verifies the kernel/tracer-injected return value equals 42, rewrites `errstr` to include `(INJECTED)`, and all command cases print success-style results.

State and persistence: No intended real BPF object creation; uses test memory buffers.

Dependencies and integration: Used by injection tests to exercise code paths that would otherwise fail due to invalid attrs or privileges.

Risks: Requires correct fault/retval injection setup; without it the helper fails on unexpected return values.

Test signals: Every BPF probe should show `= 42 (INJECTED)` style output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-success.c -->
