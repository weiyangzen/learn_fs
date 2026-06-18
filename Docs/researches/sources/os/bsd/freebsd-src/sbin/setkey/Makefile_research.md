# File Research: sources/os/bsd/freebsd-src/sbin/setkey/Makefile

## Summary
Builds the `setkey` IPsec PF_KEY utility, including its yacc parser, lex scanner, and embedded libipsec/PF_KEY support sources.

## Main Elements
- Builds `PROG=setkey` and `setkey.8`.
- Compiles `setkey.c`, `parse.y`, and `token.l`.
- Reuses `pfkey.c`, `pfkey_dump.c`, `key_debug.c`, and `ipsec_strerror.c`.
- Generates `y.tab.h` from `parse.y`.
- Enables `IPSEC_DEBUG` and `YY_NO_UNPUT`.
- Conditionally defines `INET` and `INET6`.
- Links `libipsec`.
- Has a disabled `scriptdump` script target generated from `scriptdump.pl`.

## Dependencies And Integration
Uses FreeBSD build options, yacc/lex integration, `lib/libipsec`, and `sys/netipsec` headers/sources.
