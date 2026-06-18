# sources/test-tools/liburing/test/bpf_nops.c

Purpose: userspace harness for `nops.bpf.c`, checking a BPF struct_ops loop can submit and reap 1000 NOPs. Important APIs are generated `nops_bpf` skeleton calls, `bpf_map__attach_struct_ops`, `io_uring_enter`, `t_create_ring_params`, and specialized io_uring setup flags.

Control flow: create the ring, open/configure skeleton rodata with CQ offsets and SQ/CQ sizes, set `reqs_to_run`, load and attach struct_ops, enter the ring, and verify no requests remain. State is ring kernel state plus skeleton BSS. It skips on missing BPF ops and fails on load/attach/run errors or leftover work.
