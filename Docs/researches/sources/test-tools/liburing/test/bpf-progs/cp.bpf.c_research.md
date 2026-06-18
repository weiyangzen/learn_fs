# sources/test-tools/liburing/test/bpf-progs/cp.bpf.c

Purpose: BPF struct_ops loop program that copies one file to another by submitting io_uring read/write SQEs from inside `cp_loop_step`. Important pieces are `bpf_io_uring_get_region`, `bpf_io_uring_submit_sqes`, `sqe_prep_rw`, `issue_next_req`, globals for ring offsets/file descriptors/buffer state, and exported `cp_ops`.

Control flow: submit an initial read, consume exactly one CQE at a time, turn read completions into writes, turn write completions into the next read, and stop on EOF or error via `cp_result`. State persists in BPF globals such as `cur_offset`, `nr_infligt`, and `cp_result`; integration depends on `bpf_defs.h` and the userspace skeleton. Risks include CQ wrap math, partial-write assumptions, verifier/layout drift, and BPF helper availability.
