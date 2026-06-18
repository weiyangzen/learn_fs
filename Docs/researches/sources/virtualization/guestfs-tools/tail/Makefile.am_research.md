# File Research: sources/virtualization/guestfs-tools/tail/Makefile.am

Automake file for the C-based `virt-tail` tool.

Key behavior:
- Builds `bin_PROGRAMS = virt-tail` from `tail.c`.
- Defines include paths for common utils, structs, libguestfs, options, windows support, and gnulib.
- Links common options/windows/structs/utils libraries plus guestfs, XML, libvirt, gettext, and gnulib.
- Generates `virt-tail.1` and website HTML through `PODWRAPPER` with common option path, `GPLv2+`, and `--warning safe`.
- Runs documentation and functional tail tests through `run --test`.
- Provides `check-valgrind`.

Research notes:
- Unlike resize/sparsify/sysprep, this target is implemented directly in C in this group.
