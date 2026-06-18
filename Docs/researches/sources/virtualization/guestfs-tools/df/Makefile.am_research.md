# File Research: sources/virtualization/guestfs-tools/df/Makefile.am

## Scope

Automake rules for the C-based `virt-df` tool.

## Build And Docs

- Builds `virt-df` from `virt-df.h`, `df.c`, `main.c`, and `output.c`.
- Includes common options, parallel, structs, utils, libguestfs, and gnulib headers.
- Links common libraries, libguestfs, libxml2, libvirt, gettext, gnulib, pthread, and math.
- Generates man page and website HTML from POD.

## Tests

- Runs docs and direct image tests.
- Adds libvirt guest test under `HAVE_LIBVIRT`.
- Provides valgrind targets, including one for local libvirt guests.

## Risks And Invariants

- Parallel and libvirt libraries are needed for all-domain scanning.
- Output formatting is separately implemented in `output.c` and verified by tests.
