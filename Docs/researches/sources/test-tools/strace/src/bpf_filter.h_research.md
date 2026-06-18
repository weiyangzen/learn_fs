<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf_filter.h -->
## sources/test-tools/strace/src/bpf_filter.h

Purpose: Declares the shared classic BPF filter block representation and filter-program printing entry points.

Important APIs and types: Defines `struct bpf_filter_block` with `code`, `jt`, `jf`, and `k`, plus callback typedef `print_bpf_filter_fn`. Declares `print_bpf_fprog` and `decode_bpf_fprog`.

Control flow: Header-only. Callers pass either a known program address and length to `print_bpf_fprog`, or an address to a `bpf_fprog` wrapper to `decode_bpf_fprog`.

State and persistence: No state; it is a common ABI-like contract for decoder modules.

Dependencies and integration: Requires `struct tcb` and `kernel_ulong_t` from `defs.h` context. Used by `bpf_filter.c`, `bpf_seccomp_filter.c`, and `bpf_sock_filter.c`.

Risks: The struct mirrors classic `sock_filter`; layout assumptions must remain consistent with `<linux/filter.h>`.

Test signals: Compile coverage plus callers that decode seccomp and socket BPF programs validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf_filter.h -->
