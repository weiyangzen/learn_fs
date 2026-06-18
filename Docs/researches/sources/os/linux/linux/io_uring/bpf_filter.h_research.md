# File Research: sources/os/linux/linux/io_uring/bpf_filter.h

## Purpose
Provides the io_uring BPF filter API with config-dependent stubs.

## Main Contents
- Under `CONFIG_IO_URING_BPF`:
  - `__io_uring_run_bpf_filters()`
  - `io_register_bpf_filter()`
  - `io_put_bpf_filters()`
  - `io_bpf_filter_clone()`
  - Inline `io_uring_run_bpf_filters()`.
- Without BPF support:
  - Registration returns `-EINVAL`.
  - Running filters is a no-op success.
  - Put/clone are no-ops.

## Cross-File Relationships
- Implemented by `bpf_filter.c`.
- Used by io_uring restriction setup and request validation paths.

## Risks / Review Notes
- Stub behavior means code can call filter APIs unconditionally, but registration failure semantics differ when config is disabled.
