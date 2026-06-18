# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_krb5/Makefile

Read completely: 42 lines.

This builds the `pam_krb5` module from `pam_krb5.c` and installs `pam_krb5.8`. It links against Heimdal `krb5`, `asn1`, `roken`, `com_err`, local `crypt`, and OpenSSL `crypto`.

It disables clang format-security warnings for this module and includes the common PAM module build rules via `../mod.mk`.

Security/reliability notes: build-only file. The key dependency implication is that this module is Heimdal-oriented and depends on crypto and Kerberos libraries being available in the NetBSD tree.
