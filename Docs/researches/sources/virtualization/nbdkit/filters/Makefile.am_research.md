# File Research: sources/virtualization/nbdkit/filters/Makefile.am

Purpose: top-level Automake entry for the nbdkit filter directory.

Key details:
- Includes `$(top_srcdir)/common-rules.mk`.
- Distributes `filters.syms`, the linker version script used by many filter subdirectories.
- Delegates recursive build traversal to `SUBDIRS = $(filters)`, so the actual filter set is controlled by the configured `filters` variable outside this file.

Integration notes:
- This file is pure build orchestration; adding/removing filters depends on the higher-level configure/build variables, not local hard-coded subdir names.
