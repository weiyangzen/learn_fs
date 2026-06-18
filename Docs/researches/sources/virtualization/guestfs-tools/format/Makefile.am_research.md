# File Research: sources/virtualization/guestfs-tools/format/Makefile.am

Automake rules for `virt-format`.

Build contents:
- Program: `virt-format`.
- Source: `format.c`.
- Includes common utils, libguestfs, options, fish, include, and local gnulib paths.
- Links options, utils, libguestfs, libxml2, libvirt, gettext, and `libgnu.la`.

Documentation:
- Generates `virt-format.1` and website HTML from `virt-format.pod`.

Tests:
- `test-virt-format-docs.sh`
- `test-virt-format.sh`
- Valgrind check target.

Research relevance: build wiring for destructive disk formatting tool.
