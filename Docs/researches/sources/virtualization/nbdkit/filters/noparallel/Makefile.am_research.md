# File Research: sources/virtualization/nbdkit/filters/noparallel/Makefile.am

This build file creates `nbdkit-noparallel-filter.la` from `noparallel.c`, distributes the POD manual, and optionally emits `nbdkit-noparallel-filter.1`. It uses the core include paths and standard filter module flags.

The implementation is self-contained and links only the platform import library. Build risk is low; the important dependency is the public filter API's thread-model callback contract.
