# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/Makefile

FreeBSD build file for the `ipfw` command.

Key behavior:
- Builds `ipfw` and links `dnctl` to the same binary.
- Includes core source files for ipfw, dummynet, IPv6, NAT, tables, NAT64 variants, and NPTv6.
- Adds `altq.c` and `-DPF` when `MK_PF` is enabled.
- Links against `jail` and `util`; enables tests subdir when `MK_TESTS` is set.

Research notes:
- Suppresses `-Wcast-align` warnings after including `bsd.prog.mk`.
