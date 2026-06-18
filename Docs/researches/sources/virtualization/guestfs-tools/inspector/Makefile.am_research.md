# File Research: sources/virtualization/guestfs-tools/inspector/Makefile.am

Automake rules for `virt-inspector`.

Build contents:
- Program: `virt-inspector`.
- Sources include `inspector.c` plus shared `../filesystems/utils.c` and `utils.h`.
- Includes common utils, structs, libguestfs, filesystem utils, options, fish, include, and gnulib paths.
- Links options, structs, utils, libguestfs, libxml2, libvirt, gettext, and `libgnu.la`.

Distributed fixtures:
- Example XML files for Debian, Fedora, RHEL 6, Ubuntu, Windows.
- Expected XML outputs for multiple phony/test guest images.
- Inspector tests, LUKS/LVM tests, docs test, xmllint test.

Documentation:
- Installs `virt-inspector.rng` and example XML under docs.
- Generates manpage and website HTML from POD.

Research relevance: build and test manifest for OS inspection XML generation.
