# sources/user-network-fs/samba/source3/librpc/crypto/gse_krb5.h

## Purpose
`gse_krb5.h` declares the Kerberos-specific server keytab helper used by the GSE implementation.

## Important APIs, types, and functions
- `gse_krb5_get_server_keytab(krb5_context krbctx, krb5_keytab *keytab)` returns a populated acceptor keytab for the current Samba configuration.
- The declaration is guarded by `HAVE_KRB5`, matching the implementation.

## Control flow
No runtime flow exists in the header. Build-time availability follows `HAVE_KRB5`; callers in Kerberos-enabled builds can request a keytab for importing GSS acceptor credentials.

## State and persistence behavior
The header exposes no state. Ownership expectations are conveyed through the `krb5_keytab *` out parameter: the caller must close the returned keytab.

## Dependencies and integration points
The header requires Kerberos types to be visible before inclusion. It is included by `gse.c` and implemented by `gse_krb5.c`.

## Risks and edge cases
The signature exposes raw Kerberos handles, so callers must provide an initialized context and close returned keytabs. Disabled-Kerberos builds must not compile call sites.

## Test signals
Compile both with and without `HAVE_KRB5`; run server authentication setup tests that prove returned keytabs can be imported into GSS acceptor credentials.
