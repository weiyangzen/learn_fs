# File Research: sources/virtualization/guestfs-tools/filesystems/Makefile.am

Automake rules for `virt-filesystems`.

Build contents:
- Program: `virt-filesystems`.
- Sources: `filesystems.c`, `utils.c`, `utils.h`.
- Includes common utils, structs, libguestfs, options, windows, include, and local gnulib paths.
- Links common option/windows/struct/utils libraries, libguestfs, libxml2, libvirt, gettext, and `../gnulib/lib/libgnu.la`.

Documentation:
- Generates `virt-filesystems.1` and website HTML from `virt-filesystems.pod` via `PODWRAPPER`.

Tests:
- `test-docs.sh`
- `test-virt-filesystems.sh`
- Valgrind targets, including local guest iteration.

Research relevance: captures build-time dependency boundaries for the filesystem inventory tool.
