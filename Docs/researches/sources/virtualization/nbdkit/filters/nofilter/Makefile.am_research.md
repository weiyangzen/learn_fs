# File Research: sources/virtualization/nbdkit/filters/nofilter/Makefile.am

This fragment builds a do-nothing `nbdkit-nofilter-filter.la` from `nofilter.c`, with core include paths and the normal filter module/linker flags. It distributes and optionally generates the `nbdkit-nofilter-filter.1` manual.

The module links only the platform import library because the implementation has no helper dependencies. It exists as a build/test/demo baseline for an empty filter.
