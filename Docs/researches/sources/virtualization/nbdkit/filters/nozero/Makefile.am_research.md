# File Research: sources/virtualization/nbdkit/filters/nozero/Makefile.am

This Automake fragment builds `nbdkit-nozero-filter.la` from `nozero.c`, distributes `nbdkit-nozero-filter.pod`, and conditionally generates its man page. It uses the core nbdkit include paths and standard filter module/link flags.

No common helper library is linked beyond the platform import library. The build contract is aligned with the filter's purpose as a capability and flag-shaping wrapper for zero operations.
