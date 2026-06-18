# File Research: sources/virtualization/nbdkit/filters/stats/Makefile.am

This Automake file conditionally builds the C++ `stats` filter only when `HAVE_CXX` is true. The module source is `stats.cpp` plus the public filter header, compiled as C++11 with `$(WARNINGS_MODULE_CXXFLAGS)`.

The filter includes public/generated nbdkit headers, common include files, and common utilities, then links against `common/utils/libutils.la`, `common/replacements/libcompat.la`, and the Windows import library when needed. Standard module flags and the optional `filters/filters.syms` linker script match the other filter modules.

Documentation distribution and man/HTML generation are controlled by `HAVE_POD`, producing `nbdkit-stats-filter.1` from `nbdkit-stats-filter.pod`.
