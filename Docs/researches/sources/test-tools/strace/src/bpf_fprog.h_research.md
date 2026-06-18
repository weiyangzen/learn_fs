<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf_fprog.h -->
## sources/test-tools/strace/src/bpf_fprog.h

Purpose: Defines a strace-local BPF program descriptor that can represent a tracee pointer in `kernel_ulong_t` form.

Important APIs and types: `struct bpf_fprog { unsigned short len; kernel_ulong_t filter; }`.

Control flow: Header-only; consumed by `decode_bpf_fprog`.

State and persistence: No runtime state.

Dependencies and integration: Needs `kernel_ulong_t` from `defs.h`. It avoids direct use of host `struct sock_fprog` pointer size so mpers/compat tracing remains stable.

Risks: Incorrect word-size handling would break compat tracees; the explicit `kernel_ulong_t` pointer mitigates that.

Test signals: 32-bit personality and native seccomp/socket filter tests should confirm pointer printing and array fetching remain correct.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf_fprog.h -->
