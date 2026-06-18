# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/log.c

Basic libnvme logging implementation.

Key behavior:
- `write_all()` writes a full buffer to a file descriptor, retrying on `EINTR` and `EAGAIN`.
- `__libnvme_msg()` filters by log level, builds optional timestamp/PID/function-name prefixes, formats the message, and writes it to the context log fd.
- Timestamp uses `CLOCK_MONOTONIC` unless `LOG_CLOCK` is overridden.
- Public setters/getters manage log level, PID inclusion, and timestamp inclusion.

Research notes:
- Logging assumes a valid `struct libnvme_global_ctx`; there is no NULL-context fallback here.
- If final write fails, it reports through `perror()`, not libnvme logging, avoiding recursion.
