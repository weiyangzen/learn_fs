# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/Makefile

## Purpose
Builds NetBSD's private telnet protocol support library.

## Key Elements
Defines `LIBISPRIVATE=yes`, `LIB=telnet`, base sources `auth.c encrypt.c genget.c getent.c misc.c`, enables `HAS_CGETENT`, includes the source directory, and builds DES encryption support via `enc_des.c` with `ENCRYPTION`, `AUTHENTICATION`, and `DES_ENCRYPTION`.

Kerberos support adds `kerberos5.c` when `USE_KERBEROS != no`. PAM support adds SRA sources `sra.c pk.c` when `USE_PAM != no`. Selected files suppress pointer-sign warnings.

## Dependencies
Uses NetBSD make infrastructure, telnet headers, DES, optional Kerberos, and optional PAM/OpenSSL BIGNUM support.

## Risks And Notes
Authentication and encryption are compiled in by default here. SRA is tied to PAM availability in this build logic.
