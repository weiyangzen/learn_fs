# File Research: sources/os/plan9/9front/sys/src/9/ppc/mcc.c

Incomplete/imported MPC8260 MCC2/TDM driver source.

Key responsibilities:
- Documents an MCC2 + TDM A:2 channel-128 driver for an offboard T1 framer.
- Defines HPI/FPGA/MCC constants, includes `mcc2.h`, and declares many Linux-style file operation, ioctl, interrupt, heap/list, and MCC helper prototypes.
- Implements `ioctl_parm()` for configuring SI mode and part of `mcc2_ioctl()` for mode changes and read/write access to HPI, FPGA, memory-mapped IMMR space, and SI RAM control.
- Includes Linux module/character-device style open/release/init scaffolding and copy_to_user/copy_from_user calls.

Dependencies:
- Refers to Linux kernel types/macros (`struct file`, `struct inode`, `copy_to_user`, `MOD_INC_USE_COUNT`, etc.) and `mcc2.h`, not normal Plan 9 driver interfaces.

Notable behavior:
- The file appears to be a transplanted or disabled Linux-oriented driver fragment rather than integrated Plan 9 kernel code.
