# File Research: sources/virtualization/nbdkit/filters/scan/Makefile.am

This fragment builds `nbdkit-scan-filter.la` from `scan.c`, `scan.h`, and `bgthread.c`, includes core headers and `common/utils`, and links utilities/replacements plus platform import support. It distributes and optionally builds the manual.

Only `bgthread.c` is in this work item; `scan.c` and `scan.h` belong to the next group, but this Makefile establishes the full module composition and dependencies.
