# File Research: sources/os/linux/linux/io_uring/Kconfig

## Purpose
Defines optional io_uring feature configuration symbols.

## Main Contents
- `IO_URING_ZCRX`: enabled by default when io_uring, page pool, INET, and NET_RX_BUSY_POLL are available.
- `IO_URING_BPF`: enabled by default when BPF and networking are available.
- `IO_URING_BPF_OPS`: enabled by default when io_uring, BPF syscall support, BPF JIT, and BTF debug info are available.

## Cross-File Relationships
- Controls compilation of `zcrx.o`, `bpf_filter.o`, and `bpf-ops.o` through the local Makefile.
- Feature guards match conditional code in `bpf_filter.h`, `bpf-ops.h`, and network/NAPI paths.

## Risks / Review Notes
- These are `def_bool y` feature gates driven entirely by dependencies; there are no user-visible prompts or sub-options in this file.
