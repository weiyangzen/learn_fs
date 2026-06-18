<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_util.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/gss_util.h

## Purpose
This header declares shared GSS utility functions and compatibility mappings for Kerberos-specific GSS extension APIs.

## APIs And Types
It exports `gssd_creds`, `gssd_acquire_cred`, `pgsserr`, `gssd_check_mechs`, and `gssd_cleanup`. When not using libgssglue, it maps generic lucid-context and allowable-enctype helper names onto `gss_krb5_*` functions from `gssapi_krb5.h`.

## State, Dependencies, And Integration
The header depends on RPC/GSS headers and `write_bytes.h`. It is included by gssd core, upcall processing, context serialization, and Kerberos utilities, making it the compatibility shim between libtirpc/rpcsec_gss code and concrete GSSAPI implementations.

## Risks And Test Signals
Risks include macro compatibility differences between libgssglue and direct Kerberos GSS headers, and exposing a global credential handle without ownership annotations. Test builds with libgssglue and without it, lucid support enabled, allowable-enctype support enabled, and strict warnings for macro signatures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_util.h -->
