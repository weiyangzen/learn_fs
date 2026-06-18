# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/forward.c

## Purpose
Provides Kerberos credential forwarding storage support when Kerberos is compiled.

## Main Interfaces
Defines `rd_and_store_for_creds` under `KERBEROS` or `KRB5`.

## Control Flow And State
The function decodes forwarded credentials with `krb5_rd_cred`, creates a FILE credential cache path under `/tmp/krb5cc_p<pid>`, sets `KRB5_ENV_CCNAME`, resolves and initializes the cache for the ticket client, and stores the first forwarded credential.

## Dependencies
Depends on Kerberos 5 internals/APIs, process id, environment variables, and ticket/auth-context objects.

## Risks And Notes
The credential cache path is predictable and process-id based. The file is conditionally compiled and is separate from the main `kerberos5.c` forwarding implementation used elsewhere in this group.
