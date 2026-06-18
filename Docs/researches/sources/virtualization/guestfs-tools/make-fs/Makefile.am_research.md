# File Research: sources/virtualization/guestfs-tools/make-fs/Makefile.am

## Role

Automake build file for `virt-make-fs`.

## Contents

It distributes `test-virt-make-fs.sh`, `test-virt-make-fs-docs.sh`, and `virt-make-fs.pod`; builds `virt-make-fs` from `make-fs.c`; includes common utils, structs, options, fish headers, libguestfs headers, and gnulib; and links against common libraries, libguestfs, libxml2, gettext, and gnulib.

It generates the man page and website HTML through `$(PODWRAPPER)` with GPLv2+ metadata and safe warnings. Tests include the docs test and the randomized filesystem creation test.

## Research Notes

Despite the header comment saying `virt-diff`, this Makefile builds `virt-make-fs`.
