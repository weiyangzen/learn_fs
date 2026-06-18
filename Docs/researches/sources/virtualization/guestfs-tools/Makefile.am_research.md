# File Research: sources/virtualization/guestfs-tools/Makefile.am

## Scope

Top-level Automake file for guestfs-tools. It orders common libraries, C tools, OCaml tools, Perl/bash tools, docs, translations, distribution files, clean rules, tests, and maintainer helpers.

## Build Structure

- Includes `common-rules.mk` and sets `ACLOCAL_AMFLAGS`.
- Builds shared common components first, with OCaml-only common libraries guarded by `HAVE_OCAML`.
- Adds C tools unconditionally: `align`, `cat`, `diff`, `df`, `edit`, `filesystems`, `format`, `inspector`, `log`, `ls`, `make-fs`, and `tail`.
- Adds OCaml tools only when available: `customize`, `builder`, `drivers`, `get-kernel`, `resize`, `sparsify`, and `sysprep`.
- Adds bash completion, Perl `win-reg` if enabled, docs, gettext catalogs, and optional po4a docs.

## Generated/Distribution Logic

- `EXTRA_DIST` includes repository metadata, maintainer scripts, internal headers, and support files.
- `dist-hook` regenerates translation input lists and docs POT files.
- `po/POTFILES` and `po/POTFILES-ml` are generated from source discovery with exclusions for generated, dummy, and test files.
- Builds `podwrapper.1` from `podwrapper.pl`.

## Tests And Maintenance

- Default top-level `TESTS` runs `check-mli.sh`.
- `build-test-guests` prepares phony guests.
- `check-valgrind` and `check-slow` discover subdirectories with matching targets and run them.
- Maintainer targets commit/tag the current version and check `EXTRA_DIST` completeness against git files.

## Risks And Invariants

- `SUBDIRS` ordering matters because OCaml tools depend on common OCaml libraries and customize code.
- Translation file generation depends on stable grep exclusions.
- Maintainer distribution checks assume git submodule layout and generated-file exclusions remain accurate.
