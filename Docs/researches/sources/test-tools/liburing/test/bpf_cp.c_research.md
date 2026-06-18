# sources/test-tools/liburing/test/bpf_cp.c

Purpose: userspace harness for `cp.bpf.c`, validating io_uring BPF struct_ops can drive a direct-I/O file copy. Important APIs are generated `cp_bpf` skeleton calls, `bpf_map__attach_struct_ops`, `t_create_ring_params`, `io_uring_enter`, and specialized ring flags `SINGLE_ISSUER`, `DEFER_TASKRUN`, `NO_SQARRAY`, `CQSIZE`, and `SQ_REWIND`.

Control flow: open input/output with `O_DIRECT`, stat input size, allocate aligned buffer, configure skeleton rodata/BSS with ring offsets and fds, load/attach struct_ops, truncate output, enter the ring, and check `cp_result`. State is shared with BPF through skeleton BSS and output file contents. Risks include direct-I/O setup, missing BPF ops, load/attach failures, and lack of final byte comparison.
