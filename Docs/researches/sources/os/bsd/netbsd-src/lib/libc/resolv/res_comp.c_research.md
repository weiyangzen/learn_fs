# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_comp.c

Resolver compatibility functions for DNS name compression, expansion, skipping, and name validity checks.

Important functions:
- `dn_expand()` wraps `ns_name_uncompress()` and converts root `"."` to empty string.
- `dn_comp()` wraps `ns_name_compress()`.
- `dn_skipname()` wraps `ns_name_skip()`.
- `res_hnok()`, `res_ownok()`, `res_mailok()`, and `res_dnok()` validate hostname-like, owner, mail, and domain names using explicit ASCII checks.

Under `BIND_4_COMPAT`, it also provides old put/get short/long wrappers over `ns_put16`, `ns_put32`, `ns_get16`, and `ns_get32`. The character checks deliberately avoid locale-sensitive ctype macros for DNS wire/presentation constraints.
