<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_oids.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/gss_oids.c

## Purpose
This file defines the Kerberos V5 GSS mechanism OID used throughout gssd to recognize, request, and serialize Kerberos RPCSEC_GSS contexts.

## APIs And State
It exports one global object, `gss_OID_desc krb5oid`, with length 9 and the Kerberos V5 OID byte sequence. There is no control flow or dynamic state.

## Dependencies And Integration
The file depends on GSSAPI type definitions. `context.c`, context serializers, `gss_util.c`, `gss_names.c`, and `krb5_util.c` use this OID for comparisons, desired mechanism sets, error display, and context export.

## Risks And Test Signals
Risks are low but central: if the OID bytes are wrong or object linkage is duplicated, every Kerberos mechanism check fails. Test with `gss_indicate_mechs`, OID comparison against the library's Kerberos mechanism, and link tests ensuring exactly one definition.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_oids.c -->
