# File Research: sources/os/linux/linux/io_uring/bpf-ops.h

## Purpose
Defines io_uring BPF struct-ops types and unregister hook.

## Main Contents
- Region IDs: `IOU_REGION_MEM`, `IOU_REGION_CQ`, `IOU_REGION_SQ`.
- `struct io_uring_bpf_ops` with:
  - `loop_step` callback.
  - `ring_fd` userspace-selected ring fd.
  - `priv` installed ring context pointer.
- Conditional `io_unregister_bpf_ops()` declaration or no-op stub.

## Cross-File Relationships
- Implemented by `bpf-ops.c`.
- Used by io_uring context teardown and BPF struct-ops registration.

## Risks / Review Notes
- `priv` is owned by install/uninstall paths and protected by locking rules in `bpf-ops.c`; direct consumers must not treat it as generally stable.
