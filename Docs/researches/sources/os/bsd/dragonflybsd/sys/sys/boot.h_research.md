# File Research: sources/os/bsd/dragonflybsd/sys/sys/boot.h

Read completely: 52 lines.

This header maps boot environment variable names to reboot/boot flags.

Key contents:
- Static `howto_names[]` table mapping strings like `boot_askname`, `boot_cdrom`, `boot_ddb`, `boot_gdb`, `boot_single`, `boot_verbose`, `boot_vidcons`, and `boot_serial` to `RB_*` masks.
- Null terminator entry.

Security/reliability notes:
- The table is `static` in a header, so each including translation unit receives its own copy.
- Requires `RB_*` constants to be defined before meaningful use.
