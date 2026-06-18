# File Research: sources/virtualization/guestfs-tools/sysprep/Makefile.am

Automake file for the OCaml-based `virt-sysprep` tool.

Key behavior:
- Lists all sysprep operation module names in alphabetical order and expands them into `.mli` and `.ml` source lists.
- Builds `virt-sysprep` from OCaml modules plus `dummy.c` under `HAVE_OCAML`.
- Links with guestfs, visit, structs, XML, customize, gettext, pcre, and tools support libraries.
- Autogenerates empty operation `.mli` files because operation modules export nothing.
- Generates `virt-sysprep.1` and website HTML using `PODWRAPPER`, inserting generated option and operation POD snippets.
- Generates `sysprep-extra-options.pod` from `virt-sysprep --dump-pod-options`.
- Generates `sysprep-operations.pod` from `virt-sysprep --dump-pod`.
- Runs docs, general sysprep, backup-files, passwords, and script tests.
- Provides valgrind targets, including one for local libvirt guests.

Research notes:
- This file exposes the operation inventory and generated-documentation path for `virt-sysprep`.
