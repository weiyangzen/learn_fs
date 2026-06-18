# File Research: sources/os/plan9/plan9/sys/src/9/ppc/mcc.c

MPC8260 MCC2/TDM A:2 driver fragment intended for a T1-framer interface, but it is not integrated as normal Plan 9 kernel code.

Key responsibilities visible in the file:
- Declares MCC2 ioctl/read/write/open/release-style entry points.
- Provides `ioctl_parm` to configure SI mode register loopback/echo/normal operation.
- Handles ioctl cases for MCC mode, HPI read/write, FPGA read/write, memory read/write relative to the MPC8260 internal map, and SI RAM control reads.
- Contains Linux-style character device initialization using `register_chrdev`, `struct file`, `struct inode`, `copy_to_user`, `copy_from_user`, `MOD_INC_USE_COUNT`, and `printk`.

Important behavior:
- Accesses hard-coded HPI/FPGA physical regions and the internal memory map.
- Uses a global `mcc_iorw_t` command structure type from `mcc2.h`.
- The file ends at `#else` after `#ifndef MODULE`, indicating it is either incomplete or intentionally truncated.

Dependencies:
- Includes Plan 9 headers but then references Linux kernel APIs and types not provided by the surrounding Plan 9 tree.
- Depends on `mcc2.h`, many MCC/SI/CPM types, and external routines not defined in this file.

Notable risks:
- This file is almost certainly non-buildable in the Plan 9 kernel as-is.
- Direct user-controlled physical address read/write paths would be high-risk if active.
- The incomplete preprocessor/module tail suggests source import residue rather than maintained driver code.
