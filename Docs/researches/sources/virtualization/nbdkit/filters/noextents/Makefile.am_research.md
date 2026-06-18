# File Research: sources/virtualization/nbdkit/filters/noextents/Makefile.am

This build fragment creates `nbdkit-noextents-filter.la` from `noextents.c`, includes the public/generated nbdkit headers, and wires the standard filter module flags. It distributes and optionally builds the `nbdkit-noextents-filter.1` manual.

There are no common helper libraries linked beyond the platform import library, reflecting that the implementation only changes one advertised capability.
