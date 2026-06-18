# File Research: sources/os/bsd/freebsd-src/sbin/newfs_msdos/mkfs_msdos.h

Shared interface and option schema for the FAT filesystem builder.

Key contents:
- `ALLOPTS` macro declares all supported CLI/build options with option letter, C type, field name, minimum hint, and help text.
- `struct msdos_options` expands `ALLOPTS` into fields.
- Additional bitfields record whether timestamp, volume ID, media descriptor, and hidden sectors were explicitly set.
- Declares `int mkfs_msdos(const char *, const char *, const struct msdos_options *)`.

Research notes:
- The macro is reused by `newfs_msdos.c` to generate usage text, keeping CLI help synchronized with the options structure.
