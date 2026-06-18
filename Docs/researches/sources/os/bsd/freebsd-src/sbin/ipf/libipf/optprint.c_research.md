# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optprint.c

IPv4 option-match pretty-printer.

Key behavior:
- Prints positive `opt` matches from option mask/bits.
- Prints `sec-class` matches with named security levels.
- Prints negative `not opt` clauses for mask bits not present in match bits.

Research notes:
- Knows about the duplicate `IPOPT_SECURITY` rows in `ionames[]` and skips appropriately.
