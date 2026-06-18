# File Research: sources/virtualization/guestfs-tools/configure.ac

## Scope

Autoconf entry point for guestfs-tools.

## Configure Flow

- Initializes package `guestfs-tools` version `1.55.8`.
- Defines `PACKAGE_VERSION_FULL`.
- Sets colored heading helpers for readable configure output.
- Configures auxiliary directory and requires `guestfs-test-driver`.
- Initializes Automake, silent rules, macro directory, and libtool.
- Includes m4 checks for external programs, C compiler environment, guestfs libraries, OCaml/gettext/libguestfs bindings, Perl, miscellaneous libraries, and bash completion.
- Computes substituted `SYSCONFDIR`.
- Sets compatibility conditionals required by shared common makefiles.

## Generated Outputs

- Generates `config.h`, wrapper scripts (`ocaml-dep.sh`, `ocaml-link.sh`, `podwrapper.pl`, `run`, tests functions, `virt-win-reg`), all Makefiles, repo config files, test config files, and generated OCaml config files.

## Summary

- Prints optional component summary for C tools, gettext, liblzma, OCaml tools/gettext, Perl tools, bash completion, and completion directory.

## Risks And Invariants

- Many shared `common/` Makefiles are generated from this smaller standalone project, so compatibility conditionals are defined even when disabled.
- Optional tools and tests depend heavily on configure-detected OCaml, Perl, libvirt, liblzma, libosinfo, and bash-completion support.
