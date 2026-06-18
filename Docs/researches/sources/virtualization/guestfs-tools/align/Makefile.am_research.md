# File Research: sources/virtualization/guestfs-tools/align/Makefile.am

## Scope

Automake rules for the C-based `virt-alignment-scan` tool.

## Build And Install

- Builds `bin_PROGRAMS = virt-alignment-scan` from `scan.c`.
- Includes common options, parallel, structs, utils, libguestfs headers, and gnulib.
- Links common options/parallel/structs/utils libraries, libguestfs, libxml2, libvirt, gettext, gnulib, pthread, and math support.
- Generates `virt-alignment-scan.1` and website HTML through `PODWRAPPER`.

## Tests

- Runs docs check and a direct image scan test.
- Adds libvirt guest scan test only under `HAVE_LIBVIRT`.
- Provides `check-valgrind` by rerunning check with `VG`.

## Risks And Invariants

- The binary always builds read-only partition alignment logic, while all-domain scanning depends on libvirt availability.
- The test environment uses `$(top_builddir)/run --test`, so generated library paths and test variables come from the repository wrapper.
