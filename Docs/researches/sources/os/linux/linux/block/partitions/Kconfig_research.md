# File Research: sources/os/linux/linux/block/partitions/Kconfig

Defines kernel configuration options for partition table parsers.

Key responsibilities:
- Groups options under `menu "Partition Types"`.
- Provides `PARTITION_ADVANCED` to reveal less common/foreign partition formats.
- Enables architecture-default partition formats, such as Acorn on `ARCH_ACORN`, Amiga on `AMIGA`, Atari on `ATARI`, Mac on Mac/PPC, SGI, Sun, Ultrix, and SYSV68.
- Keeps common `MSDOS_PARTITION` and `EFI_PARTITION` default-enabled.
- Adds dependencies for subformats such as BSD/Minix/Solaris/Unixware under MSDOS partition support.
- Includes command-line and device-tree fixed partition support.

Notable options in this group:
- Acorn subformats: Cumana, EESOX, ICS, ADFS, PowerTec, RISCiX.
- AIX, OSF, Amiga, Atari, IBM DASD, Mac, MSDOS, BSD, Minix, Solaris x86, Unixware, LDM, SGI, Ultrix, Sun, Karma, EFI/GPT, SYSV68, CMDLINE, and OF partitioning.

Research relevance:
- This file controls which parser objects from `block/partitions` are compiled.
- It documents expected platform associations and user-facing intent for each parser.
