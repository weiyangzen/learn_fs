# File Research: sources/virtualization/guestfs-tools/resize/Makefile.am

Automake file for the OCaml-based `virt-resize` tool.

Key behavior:
- Includes shared `subdir-rules.mk`.
- Distributes `resize.mli`, `resize.ml`, `dummy.c`, tests, and `virt-resize.pod`.
- Under `HAVE_OCAML`, builds `bin_PROGRAMS = virt-resize` using `dummy.c` as the C source and OCaml objects as link dependencies.
- Configures OCaml package paths for guestfs bindings, progress, gettext, pcre, and tools support.
- Links through `$(top_builddir)/ocaml-link.sh`.
- Generates `virt-resize.1` and website HTML through `$(PODWRAPPER)` with `--license GPLv2+` and `--warning safe`.
- Runs tests through `$(top_builddir)/run --test`: `rhbz1285847.sh`, docs check, and stochastic Perl test.

Research notes:
- The actual resize implementation is in OCaml files not in this group; this file is build/test/documentation wiring.
