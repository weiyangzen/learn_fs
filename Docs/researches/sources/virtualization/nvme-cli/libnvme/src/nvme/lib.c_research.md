# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/lib.c

Core libnvme context and transport-handle lifecycle implementation.

Key behavior:
- Creates and frees `struct libnvme_global_ctx`.
- Initializes logging file descriptor/level and list heads for hosts and MI endpoints.
- Enables ioctl probing by default.
- Derives default MI probing behavior from `LIBNVME_MI_PROBE_ENABLED`; unset means enabled, `0`, `false`, or `disable*` disable it.
- Frees fabrics state, hosts, MI endpoints, config path, application string, and context.
- Provides setters for dry-run mode, ioctl probing, passthrough submit-entry/submit-exit hooks, retry-decision hook, and default timeout.
- Opens direct Linux handles by validating `/dev/nvme*` or `/dev/ng*` names and file type:
  - controllers must be character devices
  - namespaces must be block devices
- Attempts io_uring setup for controller character devices.
- Supports special test handles named `NVME_TEST_FD` and `NVME_TEST_FD64`.
- Dispatches `mctp:` device names to MI transport setup.

Research notes:
- `libnvme_open()` creates one transport handle and chooses direct versus MI by name prefix.
- `libnvme_close()` dispatches cleanup by handle type.
- Transport type predicates are simple wrappers over handle type or `stat` mode.
- Direct handle ownership includes closing io_uring state, closing fd, and freeing the handle.
