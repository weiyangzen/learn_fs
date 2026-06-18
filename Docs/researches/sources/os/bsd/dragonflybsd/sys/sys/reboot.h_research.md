# File Research: sources/os/bsd/dragonflybsd/sys/sys/reboot.h

Reboot system call and boot flag definitions.

Key responsibilities:
- Defines reboot flags for autoboot, ask name, single-user, no sync, halt, init name, default root, debugger, read-only root, dump, miniroot, verbose, serial, CD-ROM root, poweroff, GDB, mute, selftest, pause, video, and bootinfo.
- Documents console-selection behavior: if mute, serial, and video are all unset, multi-console mode is assumed.

Important behavior:
- Flags are passed to boot code and init-related startup paths.
- `RB_AUTOBOOT` is zero.

Dependencies:
- No includes beyond guard.

Notable risks:
- Bit assignments are bootloader/kernel ABI.
- Some flags are obsolete or unused but must remain reserved for compatibility.
