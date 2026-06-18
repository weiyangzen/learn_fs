# File Research: sources/virtualization/guestfs-tools/log/Makefile.am

## Role

Automake build file for `virt-log`.

## Contents

It distributes `test-docs.sh`, `test-virt-log.sh`, and `virt-log.pod`; builds the `virt-log` binary from `log.c`; sets include paths for common utilities, structs, options, Windows helpers, libguestfs headers, and gnulib; and links against common options/structs/utils libraries, libguestfs, libxml2, libvirt, gettext, and gnulib.

It defines manpage and website HTML generation through `$(PODWRAPPER)` using GPLv2+ metadata and safe warnings. Test execution uses `$(top_builddir)/run --test` and runs the docs and functional tests. It also provides a `check-valgrind` wrapper.

## Research Notes

The file follows the standard guestfs-tools C utility build pattern.
