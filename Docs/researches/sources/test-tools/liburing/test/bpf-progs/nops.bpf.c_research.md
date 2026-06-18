# sources/test-tools/liburing/test/bpf-progs/nops.bpf.c

Purpose: BPF struct_ops loop program that keeps up to eight NOP requests in flight until `reqs_to_run` reaches zero. Key APIs are `BPF_PROG(nops_loop_step)`, `nr_to_submit`, `bpf_io_uring_get_region`, `bpf_io_uring_submit_sqes`, CQ head/tail access, and exported `nops_ops`.

Control flow: map SQ/CQ regions, fill SQEs with `IORING_OP_NOP` and a fixed token, submit them, reap CQEs with matching token, update in-flight/remain counts, and set `cq_wait_idx` before continuing. State is BPF BSS/rodata only. Risks are bad offsets, token mismatch, underflow in remaining work, short submit, or unsupported io_uring BPF ksyms.
