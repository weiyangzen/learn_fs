# File Research: sources/virtualization/nbdkit/filters/time-limit/Makefile.am

This Automake file builds the `nbdkit-time-limit-filter.la` module from `time-limit.c` and the public filter header. It uses standard filter module flags, optional `filters/filters.syms`, and links common utilities, compatibility replacements, and the platform import library.

Include paths cover public/generated headers, common include files, and common utilities. The POD file `nbdkit-time-limit-filter.pod` is distributed and, when POD support is available, converted into `nbdkit-time-limit-filter.1` and HTML documentation.

The build file has no special feature or platform guard, so the filter is built wherever the common nbdkit filter infrastructure is available.
