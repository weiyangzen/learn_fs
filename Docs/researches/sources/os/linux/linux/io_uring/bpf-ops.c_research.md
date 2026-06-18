# File Research: sources/os/linux/linux/io_uring/bpf-ops.c

## Purpose
Implements BPF struct-ops integration for io_uring loop control and exposes selected io_uring kfuncs to BPF.

## Main Functions
- BPF kfuncs:
  - `bpf_io_uring_submit_sqes()`: submits SQEs for a ring.
  - `bpf_io_uring_get_region()`: returns pointers to mapped io_uring memory/CQ/SQ regions after size validation and with `uring_lock` held.
- BPF verifier support:
  - `bpf_io_is_valid_access()`
  - `bpf_io_btf_struct_access()`
  - `bpf_io_init()`
- Struct-ops lifecycle:
  - `io_install_bpf()`: validates ring mode and installs ops into a context.
  - `bpf_io_reg()`: resolves ring fd, locks, and installs BPF ops.
  - `bpf_io_unreg()` / `io_unregister_bpf_ops()`: eject installed ops safely.
- Module init:
  - `io_uring_bpf_init()`: registers `io_uring_bpf_ops` BPF struct ops.

## Important Design Points
- BPF ops require rings without SQPOLL or IOPOLL and require `IORING_SETUP_DEFER_TASKRUN`.
- Installed ops set `ctx->loop_step`, allowing BPF to participate in ring loop progression.
- `io_bpf_ctrl_mutex` serializes global install/uninstall with per-ring `uring_lock`.
- BTF type lookup requires `struct iou_loop_params`.
- Kfunc region access is restricted to known region IDs and size-checked.

## Cross-File Relationships
- Declares the ops structure in `bpf-ops.h`.
- Uses io_uring core submission, loop, register, and memmap helpers.
- `io_unregister_bpf_ops()` is called during ring teardown to detach BPF state.

## Risks / Review Notes
- Lock ordering between `io_bpf_ctrl_mutex` and `ctx->uring_lock` is intentional; changes can introduce deadlocks.
- `bpf_io_btf_struct_access()` allows only a prefix of `iou_loop_params`; expanding BPF-visible fields requires verifier updates.
- Install rejects several ring modes, so callers must expect `-EOPNOTSUPP`.
