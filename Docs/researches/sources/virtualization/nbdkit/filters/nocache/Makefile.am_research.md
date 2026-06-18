# File Research: sources/virtualization/nbdkit/filters/nocache/Makefile.am

This Automake file builds the `nocache` filter module from `nocache.c`, installs/distributes the POD manual, and optionally generates the man page. It includes only the core nbdkit include directories needed by this small capability-shaping filter.

The library has no common helper library dependency beyond the platform import library. It applies the standard module, no-version, shared, and optional linker-script flags used by nbdkit filters.
