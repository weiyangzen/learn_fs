<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sg_io_v3.c -->
# sources/test-tools/strace/tests/ioctl_sg_io_v3.c

Purpose: tests SCSI generic `SG_IO` v3 (`struct sg_io_hdr`) decoding, including interface id validation, transfer directions, flags, iovec/data buffers, residual counts, status fields, and info flags.

Important APIs/types/functions: Guarded by `HAVE_SCSI_SG_H`; uses `scsi/sg.h`, `sys/uio.h`, `struct sg_io_hdr`, `SG_IO`, `SG_DXFER_*`, `SG_FLAG_*`, `SG_INFO_*`, `TAIL_ALLOC_OBJECT`, `fill_memory`, and iovec arrays.

Control flow: tests NULL, EFAULT, wrong interface id, partial interface id, then a valid `'S'` header with filled fields. It prints separate cases for TO_DEV, FROM_DEV, iovec transfers, direct byte buffers, TO_FROM_DEV before/after buffer display, flags combinations, residual truncation, status and driver/host fields.

State and persistence behavior: local SG header, iovec, and buffer memory only; invalid fd prevents device I/O.

Dependencies/integration points: depends on SCSI SG headers and strace SG_IO v3 decoder.

Risks and test signals: only compiles when `scsi/sg.h` is available. Passing output confirms direction-sensitive buffer decoding, iovec truncation, flags/info xlat, and fallback for invalid interface ids.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sg_io_v3.c -->
