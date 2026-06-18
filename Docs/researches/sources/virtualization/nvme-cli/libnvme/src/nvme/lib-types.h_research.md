# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/lib-types.h

Core public type definitions shared by libnvme transport, ioctl, and MI code.

Key definitions:
- Forward declares:
  - `struct libnvme_global_ctx`
  - `struct libnvme_transport_handle`
  - `struct libnvme_mi_ep`
- Defines `struct libnvme_passthru_cmd`, a platform-neutral NVMe passthrough command layout with opcode, namespace, command dwords, data/metadata pointers, lengths, timeout, and result.
- Defines `struct libnvme_uring_cmd`, the io_uring-oriented variant without result.
- Defines `libnvme_fd_t` differently by platform:
  - Windows: `HANDLE`, invalid value `INVALID_HANDLE_VALUE`
  - non-Windows: `int`, invalid value `-1`

Research notes:
- The passthrough command layout is the central ABI object used by Linux ioctl paths, Windows translations, and MI admin passthrough.
- `addr` and `metadata` are stored as `__u64`, so implementations cast through `uintptr_t` when accessing user buffers.
