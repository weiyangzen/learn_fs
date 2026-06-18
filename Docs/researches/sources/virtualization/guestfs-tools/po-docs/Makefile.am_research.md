# File Research: sources/virtualization/guestfs-tools/po-docs/Makefile.am

## Role

Top-level Automake file for translated guestfs-tools man pages and POD files.

## Contents

It reads languages from `LINGUAS` while avoiding the uppercase `LINGUAS` environment conflict, and currently treats `ja` and `uk` as translated language subdirectories. It distributes the docs POT file, all language `.po` files, and the generated `podfiles` list.

The `guestfs-tools-docs.pot` target runs `PO4A_UPDATEPO` over all POD files listed in `podfiles`. The `podfiles` target finds repository `.pod` files, excludes Debian, release-note, po-docs, and stamp files, appends Perl POD files from `po/POTFILES-pl`, sorts, and writes the list.

## Research Notes

The file notes the po4a integration is naive and separate from the main `po/` domain.
