# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ksu/Makefile

Read completely: 42 lines.

This builds `pam_ksu` from `pam_ksu.c`, installs `pam_ksu.8`, and links against Heimdal `krb5`, `asn1`, `roken`, `com_err`, local `crypt`, and OpenSSL `crypto`.

It also suppresses clang format-security warnings and includes the common PAM module rules.

Security/reliability notes: build-only file. It mirrors `pam_krb5` dependency selection for Kerberos-backed authentication.
