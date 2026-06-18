# File Research: sources/virtualization/guestfs-tools/gnulib/lib/Makefile.am

Automake rules for local vendored gnulib subset.

Builds:
- `noinst_LTLIBRARIES = libgnu.la`

Sources include:
- Argument matching, bit rotation, C-locale character classification, error fallback, `getprogname`, hash table, human-readable sizes, ignored return value helper, allocation overflow checks, and `xstrtol` variants.

Comment notes that this directory contains dependencies originally from gnulib and is intended to eventually disappear, likely by migration to `common/utils`.

Research relevance: compatibility and utility substrate used by multiple guestfs tools.
