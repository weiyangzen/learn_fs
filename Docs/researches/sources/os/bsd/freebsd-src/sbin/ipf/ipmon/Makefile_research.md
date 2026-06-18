# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipmon/Makefile

This Makefile builds the `ipmon` log monitor.

Key points:
- `PROG=ipmon`, `PACKAGE=ipf`.
- Sources are generated headers plus `ipmon.c`, `ipmon_y.c`, and `ipmon_l.c`.
- Installs `ipmon.5` and `ipmon.8`, with `ipmon.conf.5` linked to `ipmon.5`.
- Adds `-DLOGFAC=LOG_LOCAL0 -I.` and suppresses `unused-but-set-variable` as an error.
- Generates parser and lexer sources by yacc/sed and sed-rewriting common lexer names from `yy` to `ipmon_yy`.

The program uses the shared lexer source with an IPMon-specific yacc grammar.
