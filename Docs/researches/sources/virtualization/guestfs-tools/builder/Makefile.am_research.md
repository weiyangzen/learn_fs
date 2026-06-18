# File Research: sources/virtualization/guestfs-tools/builder/Makefile.am

## Scope

Automake rules for `virt-builder`, `virt-builder-repository`, the C `virt-index-validate` validator, parser tests, repository config, templates, docs, and builder test images.

## Build Structure

- Lists OCaml interfaces/implementations for builder, cache, downloader, index parsing, sources, Simplestreams, list output, and command-line handling.
- Lists C parser/support sources: flex scanner, bison parser, structure ownership, OCaml parser bridge, pxzcat bridge, and setlocale bridge.
- Under `HAVE_OCAML`, builds `virt-builder`, `virt-builder-repository`, and `index_parser_tests` with `ocaml-link.sh`.
- Links shared OCaml archives from common utility, gettext, XML, guestfs, tools, and customize libraries.
- Generates `osinfo_config.ml` from the configured libosinfo database path.

## Data And Docs

- Installs default repo config files and GPG keys under `virt-builder/repos.d`.
- Generates man pages and website HTML for `virt-builder`, `virt-builder-repository`, and `virt-index-validate`.
- Builds compressed/qcow2 phony guest artifacts for tests when source images exist.

## Tests

- Standard tests cover docs, cache-all, list output, index validation, Simplestreams list output, core virt-builder behavior, and parser tests.
- Slow tests cover serial console boot checks, planner combinations, and repository generation/update behavior.
- Console wrapper scripts are generated from a common `test-console.sh`.

## Risks And Invariants

- Parser-generated files are built but removed from the distribution by `dist-hook`.
- OCaml link ordering and common library archives are significant.
- Many tests depend on generated phony guests, qemu-img, xz, libguestfs runtime wrappers, and optional OCaml/native compiler availability.
