# File Research: sources/os/bsd/netbsd-src/lib/libipsec/Makefile

NetBSD build file for `libipsec`, sourced from imported `crypto/dist/ipsec-tools`.

It builds policy and PF_KEY helpers, parser/lexer sources, and debug support. It enables Fortify for a network protocol library, shared-lib install directory behavior, `IPSEC_DEBUG`, and conditional `INET6`. It sets yacc/lex prefixes to avoid symbol collisions and installs `ipsec_set_policy.3` links.
