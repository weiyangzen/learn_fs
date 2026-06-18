<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-v.c -->
## sources/test-tools/strace/tests/bpf-v.c

Purpose: Verbose variant of the BPF syscall decoder test.

Important APIs/types/functions: Defines `VERBOSE 1` and includes `bpf.c`.

Control flow: Compiles the common BPF command matrix so dynamic arrays, buffers, and extra attr bytes are printed in expanded form instead of ellipses or raw pointers.

State and persistence: Same as `bpf.c`; wrapper-local state is absent.

Dependencies and integration: Provides the `-v` expected-output lane and is also included by `bpf-success-v.c`.

Risks: Verbose output is most sensitive to formatting and kernel/uapi table drift.

Test signals: Expected output includes quoted hex data, decoded instruction arrays, iter/kprobe arrays, and explicit extra bytes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-v.c -->
