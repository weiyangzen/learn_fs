# File Research: sources/virtualization/guestfs-tools/customize/Makefile.am

## Scope

Automake rules for the OCaml-based `virt-customize` tool and its tests.

## Build And Docs

- Distributes OCaml source/interface, dummy C source, tests, and POD.
- Under `HAVE_OCAML`, builds `virt-customize` using `dummy.c` plus OCaml object files linked through `ocaml-link.sh`.
- Links common OCaml utility, guestfs, gettext, PCRE, XML, tools, and customize archives.
- Generates `virt-customize.1` and website HTML with inserted common customize synopsis/options.

## Tests

- Standard tests cover docs and phony guest customization.
- Slow tests are generated wrappers for password and settings tests across many distro templates.
- `check-slow` runs only slow tests with `SLOW=1`.

## Risks And Invariants

- `dummy.c` is needed because Automake expects a C source for the linked program.
- Generated slow-test wrappers and cleanup patterns must stay aligned with script naming.
- OCaml dependency generation uses `.depend`.
