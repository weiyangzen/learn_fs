# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/DECHanyu/Makefile

Builds the DECHanyu i18n module. It sets `SRCPRE=citrus_`, causing the common include logic to derive `citrus_dechanyu.c` from the directory basename.

It includes `bsd.lib.mk`.
