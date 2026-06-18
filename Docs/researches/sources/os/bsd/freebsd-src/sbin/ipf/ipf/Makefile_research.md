# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipf/Makefile

## Purpose
Builds the `ipf` command.

## Main Elements
- Sets `PACKAGE=ipf`, `PROG=ipf`, manuals, and manpage links.
- Builds `ipf.c`, `ipfcomp.c`, generated `ipf_y.c`, generated `ipf_l.c`, and `bpf_filter.c`.
- Enables `IPFILTER_BPF` and `HAS_SYS_MD5_H`.
- Generates parser and lexer sources by running yacc and rewriting `yy` symbols to `ipf_yy`.
- Links `libpcap` outside rescue builds.

## Dependencies And Integration
Connects common parser/lexer sources to the `ipf` utility with renamed yacc/lex symbols to avoid collisions.

## Risk Notes
The sed-based symbol rewrite is simple but broad; generated parser/lexer naming depends on these substitutions staying valid.
