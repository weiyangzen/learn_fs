<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf_filter.c -->
## sources/test-tools/strace/src/bpf_filter.c

Purpose: Decodes classic BPF filter programs and provides shared code-name printing for classic BPF and eBPF instruction classes.

Important APIs and types: Exports `print_bpf_filter_code`, `print_bpf_fprog`, and `decode_bpf_fprog`. Uses `struct bpf_filter_block_data` to track optional `k` formatting callback and printed instruction count.

Control flow: `print_bpf_filter_code` decomposes the `code` field into class, size, mode, source, operation, return value, and miscellaneous bits using classic or extended xlat tables. `decode_bpf_fprog` fetches a `struct bpf_fprog`, prints `len`, then delegates array printing to `print_bpf_fprog`. `print_bpf_filter_block` stops at `BPF_MAXINSNS`, chooses `BPF_JUMP` formatting if `jt` or `jf` are non-zero, otherwise prints `BPF_STMT`.

State and persistence: No global state. Per-array state is held in `bpf_filter_block_data.count` to enforce the instruction cap.

Dependencies and integration: Depends on `defs.h`, `bpf_filter.h`, `bpf_fprog.h`, `<linux/filter.h>`, and BPF/eBPF xlat tables. It is reused by seccomp and socket filter decoders, and by `bpf.c` for eBPF instruction code printing.

Risks: Correctness depends on interpreting classic and extended op bits differently in shared code. If kernel BPF macros or xlat tables change, unknown flag bits can be printed as `BPF_???`.

Test signals: Tests should feed statement-only filters, jump filters, max-insn boundary cases, abbrev mode, custom `k` printers from seccomp/socket wrappers, and eBPF code paths through `print_bpf_filter_code(..., true)`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf_filter.c -->
