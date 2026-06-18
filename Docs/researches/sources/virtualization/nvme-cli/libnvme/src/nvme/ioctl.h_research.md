# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl.h

Public declarations for libnvme direct ioctl/passthrough operations.

Key definitions:
- `NVME_DEFAULT_IOCTL_TIMEOUT` is `0`, meaning kernel/default timeout.
- `NVME_LOG_PAGE_PDU_SIZE` is `4096`, used as a safe log transfer chunk size.
- Declares synchronous submit/exec APIs for admin and I/O passthrough.
- Declares async passthrough queue/reap/wait APIs and `struct libnvme_passthru_completion`.
- Declares controller/namespace management helpers:
  - subsystem reset
  - controller reset
  - namespace rescan
  - namespace ID retrieval
  - block size update

Research notes:
- The header is Linux-described, but its public API is also implemented by platform-specific files such as `ioctl-win.c`.
- Async comments note io_uring sharing for Linux, so direct async use and synchronous execution should not be mixed on one handle when io_uring is active.
