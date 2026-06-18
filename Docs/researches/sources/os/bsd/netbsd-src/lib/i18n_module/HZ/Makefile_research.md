# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/HZ/Makefile

Builds the HZ i18n module. It explicitly sets `SRCS=citrus_hz.c citrus_prop.c`.

The extra `citrus_prop.c` dependency mirrors BIG5’s property-table support.
