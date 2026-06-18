# File Research: sources/virtualization/guestfs-tools/cat/Makefile.am

## Scope

Automake rules for the C-based `virt-cat` tool.

## Build And Docs

- Builds `virt-cat` from `cat.c`.
- Includes common utils, structs, options, Windows path helpers, libguestfs, and gnulib.
- Links options, windows, structs, utils, libguestfs, libxml2, libvirt, gettext, and gnulib.
- Generates `virt-cat.1` and website HTML from POD.

## Tests

- Runs docs check and `test-virt-cat.sh`.
- Supports valgrind by rerunning check with `VG`.

## Risks And Invariants

- Windows helper linkage is required because runtime path conversion is in `cat.c`.
- Tests rely on phony Fedora guest content.
