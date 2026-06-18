# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/Makefile.inc

This make include configures SH3 libc architecture sources. It adds `__sigtramp2.S`, includes the architecture directory, and when softfloat is enabled defines `SOFTFLOAT` and includes the shared softfloat build rules.

A commented `SOFTFLOAT_NEED_FIXUNS` hint shows a possible port-specific conversion need. The file is build configuration only.
