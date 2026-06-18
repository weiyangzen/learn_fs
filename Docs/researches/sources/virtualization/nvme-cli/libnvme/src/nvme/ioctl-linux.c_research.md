# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl-linux.c

Linux ioctl transport implementation for direct NVMe admin/I/O passthrough and controller management operations.

Controller/block operations:
- `nvme_verify_chr()` ensures a transport fd is a character device.
- `libnvme_reset_subsystem()`, `libnvme_reset_ctrl()`, and `libnvme_rescan_ns()` issue libnvme reset/rescan ioctls after character-device verification.
- `libnvme_get_nsid()` reads namespace ID with `LIBNVME_IOCTL_ID`.
- `libnvme_update_block_size()` applies `BLKBSZSET` and triggers `BLKRRPART`.

Passthrough submission:
- `libnvme_submit_passthru32()` adapts `libnvme_passthru_cmd` into the legacy 32-bit-result ioctl structure.
- `libnvme_submit_passthru64()` sends the command directly through the 64-bit-result ioctl.
- I/O path probes 64-bit ioctl first unless probing is disabled, caches success/fallback state, and falls back to 32-bit on `-ENOTTY`.
- Admin path follows the same 64/32 probing, but rejects fabrics admin commands on the 32-bit fallback with `-ENOTSUP`.
- Submit hooks `submit_entry`, `submit_exit`, and `decide_retry` are invoked around ioctl attempts.

Synchronous exec:
- `libnvme_exec_admin_passthru()` and `libnvme_exec_io_passthru()` prefer io_uring async submission/reap when available, falling back to ioctl submission on `-ENOTSUP` or unavailable io_uring.
- Both return completion status for async execution, or ioctl error/status from direct submission.

Dependencies:
- Linux ioctl constants, block ioctls, CCAN helpers, libnvme private transport handle state, and async passthrough functions from the uring layer.

Risks and tests:
- `libnvme_get_nsid()` uses `errno` after ioctl return rather than checking a negative return directly; tests should cover ioctl returning `-1` and unusual valid IDs.
- Passthrough probing mutates cached state in the transport handle, so concurrent use of one handle needs external safety if required.
- Dry-run mode still invokes submit hooks but skips ioctl.
- Tests should cover 64-bit ioctl success, `ENOTTY` fallback, retry callback behavior, timeout defaulting, dry-run, MI admin passthrough routing, and io_uring fallback.
