# File Research: sources/virtualization/nbdkit/filters/offset/Makefile.am

This fragment builds `nbdkit-offset-filter.la` from `offset.c`, distributes its POD, and optionally generates the man page. It includes core nbdkit headers plus `common/utils`, then links `libutils.la`, compatibility replacements, and the platform import library.

The module uses the standard filter link flags and optional linker script. Its helper dependency supports parsing/cleanup utilities used by the offset implementation.
