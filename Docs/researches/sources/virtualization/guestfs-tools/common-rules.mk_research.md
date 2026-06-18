# File Research: sources/virtualization/guestfs-tools/common-rules.mk

## Scope

Top-level shared Automake fragment included by `Makefile.am`.

## Behavior

- Optionally includes `$(top_builddir)/localenv`.
- Defines `NULL` as a list terminator helper.
- Initializes common `CLEANFILES` for editor backups, patch rejects/originals, OCaml build artifacts, generated man pages, POD stamp files, and bindtests temp files.
- Initializes `DISTCLEANFILES` for `.depend` and `stamp-*`.
- Adds OCaml and PO suffixes.

## Risks And Invariants

- Intended for top-level inclusion; comments distinguish it from `subdir-rules.mk`.
- Broad clean patterns assume no subdirectory has files matching these patterns that must survive `make clean`.
