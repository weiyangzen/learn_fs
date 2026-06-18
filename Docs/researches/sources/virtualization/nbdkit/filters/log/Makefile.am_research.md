# File Research: sources/virtualization/nbdkit/filters/log/Makefile.am

Automake rules for `nbdkit-log-filter.la`, disabled on Windows because the implementation requires `open_memstream`.

Builds `log.c`, `log.h`, `output.c`, and the public filter header. Links common utils and the Windows import hook, with standard nbdkit include paths, module/shared flags, and optional filter linker script. POD man page generation is conditional.
