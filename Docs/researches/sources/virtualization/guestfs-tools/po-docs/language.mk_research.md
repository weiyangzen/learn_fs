# File Research: sources/virtualization/guestfs-tools/po-docs/language.mk

## Role

Shared Automake logic for each translated documentation language.

## Contents

It derives `LINGUA` from the current directory name, cleans generated `.pl` and `.pod` files, defines the translated manpage set for guestfs tools, and distributes both translated manpages and generated POD files.

`all-local` builds all manpages. Special `PODWRAPPER` rules handle inserted snippets for `virt-builder`, `virt-customize`, and `virt-sysprep`; the generic `%.1: %.pod` rule handles other tools.

The `%.pod` rule runs `PO4A_TRANSLATE` using the language `.po`, selects the original POD path from `po-docs/podfiles`, writes a temporary translated POD, removes po4a’s unwanted header up through `=encoding`, and leaves the cleaned POD. The install hook places translated `.1` pages under `$(mandir)/$(LINGUA)/man1`.

## Research Notes

This file is the core translated documentation build pipeline.
