# File Research: sources/virtualization/nbdkit/filters/readonly/Makefile.am

This fragment builds `nbdkit-readonly-filter.la` from `readonly.c`, includes core headers and `common/utils`, and links utilities, replacements, and platform import support. It distributes and optionally builds the manual.

The build dependencies are modest; the implementation primarily uses the nbdkit filter API and POSIX `access`.
