# File Research: sources/virtualization/guestfs-tools/ls/Makefile.am

## Role

Automake build file for `virt-ls`.

## Contents

It distributes `test-docs.sh`, `test-virt-ls.sh`, and `virt-ls.pod`; builds `virt-ls` from `ls.c`; sets include paths for common utilities, structs, visit traversal helpers, options, Windows helpers, libguestfs headers, and gnulib; and links the common libraries plus libguestfs, libxml2, libvirt, gettext, and gnulib.

It generates `virt-ls.1` and website HTML with `$(PODWRAPPER)` and registers the documentation and functional tests under `$(top_builddir)/run --test`.

## Research Notes

The key distinction from nearby C tools is the extra dependency on `common/visit` for recursive `-lR` traversal.
