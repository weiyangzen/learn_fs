# sources/test-tools/liburing/test/bpf_defs.h

Purpose: BPF-side ABI header for io_uring struct_ops tests. It defines `io_ring_ctx`, `iou_loop_params`, region IDs, loop return constants, `io_uring_bpf_ops`, and weak ksym declarations for `bpf_io_uring_get_region` and `bpf_io_uring_submit_sqes`.

Control flow: header-only; BPF programs include it to get ring layouts and helper prototypes. It has no runtime state, but it is the contract tying BPF object code to kernel io_uring struct_ops and liburing SQE/CQE layouts. Main risk is ABI/layout drift causing verifier failures or bad ring-region interpretation.
