# File Research: sources/virtualization/nbdkit/filters/openonce/Makefile.am

This Automake file builds `nbdkit-openonce-filter.la` from `openonce.c`, distributes its POD, and conditionally generates the man page. It uses nbdkit include paths plus `common/utils`, and links utilities, replacements, and the platform import library.

The file enables standard filter module semantics and optional linker-script export filtering. Its linked helpers support cleanup/vector usage in the implementation.
