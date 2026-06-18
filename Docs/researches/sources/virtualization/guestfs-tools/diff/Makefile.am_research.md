# File Research: sources/virtualization/guestfs-tools/diff/Makefile.am

## Scope

Automake rules for the C-based `virt-diff` tool.

## Build And Docs

- Builds `virt-diff` from `diff.c`.
- Includes common utils, visit traversal, options, cat/fish headers, libguestfs, and gnulib.
- Links options, visit, structs, utils, libguestfs, libxml2, libvirt, gettext, and gnulib.
- Generates man page and website HTML from POD.

## Tests

- Runs docs check and `test-virt-diff.sh`.
- Provides valgrind check wrapper.

## Risks And Invariants

- Depends on the common visit library for recursive guest traversal.
- Runtime content diffs also depend on the external `diff` command.
