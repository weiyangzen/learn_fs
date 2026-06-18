<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_gensec_bind.h -->
# sources/user-network-fs/samba/source3/lib/tldap_gensec_bind.h

## Purpose
This header declares the GENSEC-backed LDAP bind API for source3 users.

## Important APIs, types, and functions
It forward declares `tevent_context`, `tldap_context`, `cli_credentials`, and `loadparm_context`, then exposes async `tldap_gensec_bind_send`, receive `tldap_gensec_bind_recv`, and synchronous `tldap_gensec_bind`. Parameters identify LDAP context, credentials, target service/hostname/principal, loadparm configuration, and requested GENSEC features.

## Control flow
Callers start with the send function in an existing event loop and finish with the recv function, or use the synchronous wrapper which creates and polls a temporary event context.

## State and persistence behavior
The header itself has no state. Its contract permits the implementation to mutate the LDAP context by installing a GENSEC stream when sign or seal is negotiated.

## Dependencies and integration points
It is consumed by LDAP client setup code that wants SPNEGO/SASL authentication without depending on implementation internals.

## Risks and edge cases
Callers must pass target identity accurately for Kerberos service principal selection and must understand that requested sign/seal may alter the active stream.

## Test signals
Compile coverage verifies exported signatures. Integration tests should exercise async and sync paths with different GENSEC feature flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_gensec_bind.h -->
