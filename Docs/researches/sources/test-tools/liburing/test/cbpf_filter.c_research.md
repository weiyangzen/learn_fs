# sources/test-tools/liburing/test/cbpf_filter.c

Purpose: comprehensive suite for classic BPF filters restricting io_uring operations at task and ring level. Important APIs/types are `struct io_uring_bpf`, task/ring filter registration helpers, `IORING_REGISTER_BPF_FILTER`, `IO_URING_BPF_FILTER_DENY_REST`, `IO_URING_BPF_FILTER_SZ_STRICT`, cBPF `sock_filter`, and `PR_SET_NO_NEW_PRIVS`.

Control flow: define context offsets and endian-safe constants, register filters for NOP/socket/open/openat2/connect policies, run task-level tests in child processes, conditionally run connect filters, run ring-level filters and pdu-size validation, and verify inheritance/stacking/cannot-loosen semantics across forks. State is per-task inherited restrictions and per-ring filters. Risks are feature/layout drift, endian bugs, incorrect `-EACCES`, policy loosening, or pdu_size mismatch.
