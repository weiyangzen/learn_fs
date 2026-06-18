# File Research: sources/os/linux/linux/block/partitions/Makefile

Builds the block partition parser objects according to Kconfig selections.

Key contents:
- Always builds `core.o` when `CONFIG_BLOCK` is enabled.
- Conditionally builds parser objects for Acorn, Amiga, Atari, AIX, cmdline, Mac, LDM, MSDOS, OF, OSF, SGI, Sun, Ultrix, IBM, EFI, Karma, and SYSV68 partition formats.

Research relevance:
- This is the compile-time binding between partition Kconfig symbols and parser source files.
- It confirms that the files in this group are individually optional parser modules within the built-in block partition subsystem.
