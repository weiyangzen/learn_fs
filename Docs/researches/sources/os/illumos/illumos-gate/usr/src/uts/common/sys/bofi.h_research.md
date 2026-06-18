# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bofi.h

This is the public ioctl/data contract for the bus-ops fault injector. It defines ioctl command numbers for adding/deleting definitions, start/stop, state checks, broadcasts, clearing logs/errors/definitions, and enumerating handles.

It declares access logging records (`acc_log_elem`, `acc_log` plus 32-bit form), error definitions (`bofi_errdef`), control requests, handle enumeration structures, handle metadata, operation types (`BOFI_EQUAL`, `BOFI_AND`, `BOFI_NO_TRANSFER`, interrupt manipulation modes, etc.), access types (`BOFI_PIO_*`, `BOFI_DMA_*`, `BOFI_INTR`, `BOFI_LOG`), and returned error state (`bofi_errstate`). Several structures have `_SYSCALL32` variants and explicit packing guards for mixed alignment.
