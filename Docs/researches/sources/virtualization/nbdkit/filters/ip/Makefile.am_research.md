# File Research: sources/virtualization/nbdkit/filters/ip/Makefile.am

Automake rules for `nbdkit-ip-filter.la`. Builds `ip.c`, `rules.c`, `rules.h`, and the public filter header.

Uses nbdkit/common include paths, common utils, compatibility replacements, Windows import hook, module/shared flags, and optional filter linker script. Generates `nbdkit-ip-filter.1` from POD when available.
