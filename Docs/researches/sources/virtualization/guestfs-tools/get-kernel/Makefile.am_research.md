# File Research: sources/virtualization/guestfs-tools/get-kernel/Makefile.am

Automake rules for OCaml-based `virt-get-kernel`.

Structure:
- Always distributes OCaml interface/source files and `dummy.c`.
- Builds `virt-get-kernel` only under `HAVE_OCAML`.
- Uses `dummy.c` as the C source anchor for an OCaml-linked binary.
- Defines OCaml package flags for `str`, `unix`, `guestfs`, gettext when available, and multiple common OCaml helper libraries.
- Links through `ocaml-link.sh`, selecting bytecode or native objects depending on `HAVE_OCAMLOPT`.

Documentation and tests:
- Generates `virt-get-kernel.1` and website HTML from POD.
- Runs `test-virt-get-kernel-docs.sh`.

Research relevance: records mixed C/OCaml build integration for a guest kernel extraction tool.
