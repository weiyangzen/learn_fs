<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_scsi.c -->
# sources/test-tools/strace/tests/ioctl_scsi.c

Purpose: tests legacy SCSI generic ioctl command decoding outside the `SG_IO` v3/v4 focused tests.

Important APIs/types/functions: Guarded by `HAVE_SCSI_SG_H`; uses `scsi/sg.h`, xlat `scsi_sg_commands.h`, and macros for no-arg, NULL-arg, int-by-value, and int-by-pointer command forms. It covers commands such as sg driver id/version, timeout, reserved size, low DMA, scatter-gather tables, queue depth, command queuing, dxfer, and other `SG_*` controls.

Control flow: compiles to a skip main when SCSI headers are unavailable. Otherwise it allocates integer buffers, issues each command on fd `-1`, and prints command-specific expected EBADF output with decoded scalar or pointer arguments.

State and persistence behavior: local integers only; invalid fd prevents SCSI device state changes.

Dependencies/integration points: depends on SCSI generic UAPI and strace xlat tables.

Risks and test signals: header availability and command deprecation can affect coverage. Passing output confirms names and argument shapes for classic SCSI generic ioctls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_scsi.c -->
