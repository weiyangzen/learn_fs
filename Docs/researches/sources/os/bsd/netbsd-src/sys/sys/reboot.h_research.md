# File Research: sources/os/bsd/netbsd-src/sys/sys/reboot.h

Read completely: 124 lines.

This header defines reboot and bootloader flag constants. It includes `RB_*` system reboot flags, `AB_*` autoboot verbosity/debug flags, architecture-specific high-bit `RB_MD*` flags, and old boot-device-number encoding macros.

Key macros include `MAKEBOOTDEV`, `B_ADAPTOR`, `B_CONTROLLER`, `B_UNIT`, `B_PARTITION`, and `B_TYPE`. Kernel consumers get the non-returning `kern_reboot(int, char *)` and `cpu_reboot(int, char *)` prototypes.

Risks: this is an ABI/control-plane header. Flag values and boot-device bit layouts must remain stable for bootblocks, kernel initialization, and compatibility code.
