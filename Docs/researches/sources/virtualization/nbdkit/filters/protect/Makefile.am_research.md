# File Research: sources/virtualization/nbdkit/filters/protect/Makefile.am

This fragment builds `nbdkit-protect-filter.la` from `protect.c`, distributes its POD, and optionally generates the manual. It includes the core headers plus `common/regions`, `common/replacements`, and `common/utils`.

The module links `libregions.la`, `libutils.la`, compatibility replacements, and the platform import library. Those dependencies match the implementation's range/region conversion and compatibility helper usage.
