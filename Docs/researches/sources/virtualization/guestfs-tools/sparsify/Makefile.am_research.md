# File Research: sources/virtualization/guestfs-tools/sparsify/Makefile.am

Automake file for the OCaml-based `virt-sparsify` tool.

Key behavior:
- Distributes OCaml interfaces/implementations, `dummy.c`, tests, and `virt-sparsify.pod`.
- Under `HAVE_OCAML`, builds `virt-sparsify`.
- Configures OCaml package paths for guestfs, progress, gettext, pcre, and tools support.
- Generates manpage and website HTML through `PODWRAPPER`, using common options include path, `GPLv2+`, and `--warning general`.
- Runs docs, copy-mode sparsify, and in-place sparsify tests.
- Provides `check-valgrind`.

Research notes:
- The actual sparsify logic is in OCaml files outside this batch; this file defines build and verification wiring.
