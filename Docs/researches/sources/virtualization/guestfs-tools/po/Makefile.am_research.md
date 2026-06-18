# File Research: sources/virtualization/guestfs-tools/po/Makefile.am

## Role

Main gettext Automake file for guestfs-tools program translations.

## Contents

It defines gettext domain `$(PACKAGE_NAME)`, copyright holder, Bugzilla msgid address, language list from `LINGUAS`, source file lists from `POTFILES`, `POTFILES-pl`, and `POTFILES-ml`, and generated `.po`/`.gmo` files.

When GNU gettext is available, it defines `XGETTEXT_ARGS` for C-style and Perl extraction, fixes placeholder charset values to UTF-8, optionally extracts OCaml strings through `OCAML_GETTEXT`, runs `xgettext` over C and Perl file lists, and emits `$(DOMAIN).pot`.

The `.po.gmo` rule compiles translations with `msgfmt`. The install hook installs `.mo` files under `$(datadir)/locale/$lang/LC_MESSAGES/$(DOMAIN).mo`.

## Research Notes

This is separate from `po-docs`; it covers translatable UI/program strings rather than manpage/POD translations.
