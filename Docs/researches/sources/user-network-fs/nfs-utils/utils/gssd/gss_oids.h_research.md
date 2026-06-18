<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_oids.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/gss_oids.h

## Purpose
This header exposes the Kerberos mechanism OID and provides a local OID equality macro when the GSS library does not provide one.

## APIs And Types
It declares `extern gss_OID_desc krb5oid`. `g_OID_equal` compares OID length and byte contents using `memcmp`, preserving compatibility with older GSS headers.

## State, Dependencies, And Integration
The header has no state but assumes `gss_OID_desc` and `memcmp` are visible through surrounding includes. It is included in context dispatch, serializers, GSS utilities, name conversion, and Kerberos credential logic.

## Risks And Test Signals
Risks include missing direct includes for GSSAPI/string declarations and macro double-evaluation of arguments if callers pass expressions. Test strict compile modes, equality with Kerberos and non-Kerberos OIDs, null avoidance at callers, and compatibility with headers that already define `g_OID_equal`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_oids.h -->
