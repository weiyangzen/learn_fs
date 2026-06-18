# File Research: sources/virtualization/nbdkit/filters/multi-conn/Makefile.am

This fragment builds `nbdkit-multi-conn-filter.la` from `multi-conn.c`, distributes its POD manual, and creates the manual page through the shared POD wrapper when enabled. Include paths cover nbdkit public headers, generated headers, `common/include`, and `common/utils`.

It links `libutils.la`, compatibility replacements, and the Windows import library, then uses module/no-version/shared libtool flags with optional linker-script export restriction. The file is purely build glue for the multi-connection consistency filter.
