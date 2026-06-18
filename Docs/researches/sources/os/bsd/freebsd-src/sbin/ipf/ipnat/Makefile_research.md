# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipnat/Makefile

This Makefile builds the `ipnat` command.

Key points:
- `PROG=ipnat`, `PACKAGE=ipf`.
- Sources are generated headers plus `ipnat.c`, `ipnat_y.c`, and `ipnat_l.c`.
- Installs `ipnat.8`, `ipnat.4`, and `ipnat.5`, with `ipnat.conf.5` linked to `ipnat.5`.
- Adds `-I.` and suppresses `unused-but-set-variable` as an error.
- Generates yacc output from `ipnat_y.y`, then sed-rewrites `yy` symbols to `ipnat_yy`.
- Generates lexer output from shared `lexer.c`, sed-rewriting includes and symbols for IPNAT-specific names.

This is the FreeBSD build glue for NAT rule parsing and NAT table inspection.
