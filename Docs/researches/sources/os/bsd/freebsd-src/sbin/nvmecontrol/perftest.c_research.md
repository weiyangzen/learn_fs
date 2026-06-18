# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/perftest.c

Purpose: Implements low-level NVMe performance testing through kernel test ioctls.

Key behavior:
- Registers top-level `perftest`.
- Accepts operation type, interrupt mode, thread count, transfer size, test duration, optional `refthread` flag, and per-thread reporting.
- Maps operation strings to `NVME_OPC_READ` or `NVME_OPC_WRITE`.
- Chooses `NVME_IO_TEST` or `NVME_BIO_TEST` based on interrupt mode aliases.
- Requires 1-128 threads and nonzero duration.
- Prints aggregate IOPS and MB/s, with optional per-thread IOPS.

Dependencies:
- `struct nvme_io_test`, `NVME_IO_TEST`, and `NVME_BIO_TEST` from FreeBSD NVMe interfaces.
- `open_dev()` from the shared core.

Research notes:
- This command depends on kernel support for synthetic NVMe test ioctls rather than issuing ordinary user I/O.
