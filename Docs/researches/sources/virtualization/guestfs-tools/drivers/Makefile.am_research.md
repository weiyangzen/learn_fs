# File Research: sources/virtualization/guestfs-tools/drivers/Makefile.am

## Scope

Automake rules for the OCaml-based `virt-drivers` tool.

## Build And Docs

- Distributes OCaml sources/interfaces, dummy C source, expected XML outputs, tests, and POD.
- Under `HAVE_OCAML`, builds `virt-drivers` from OCaml objects linked through `ocaml-link.sh`.
- Links common OCaml stdutils, guestfs, gettext, PCRE, utils, tools, and mldrivers archives.
- Generates `virt-drivers.1` and website HTML from POD.
- Generates OCaml dependencies into `.depend`.

## Tests

- Runs docs, Linux output, and Windows output tests under the test wrapper.

## Risks And Invariants

- `hwdata_config.ml` is configure-generated and determines optional PCI/USB IDs lookup paths.
- Expected XML tests ignore generated-by comments and normalize optional hwdata names.
