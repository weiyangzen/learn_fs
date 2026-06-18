# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/BIG5/Makefile

Builds the BIG5 i18n loadable module. Unlike most peers, it explicitly sets `SRCS=citrus_big5.c citrus_prop.c`.

It includes `bsd.lib.mk`, inheriting common i18n module settings from the parent `Makefile.inc`.
