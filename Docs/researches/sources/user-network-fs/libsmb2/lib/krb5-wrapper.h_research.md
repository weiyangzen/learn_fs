# sources/user-network-fs/libsmb2/lib/krb5-wrapper.h

## Purpose
`krb5-wrapper.h` declares the Kerberos/GSSAPI authentication interface used by libsmb2 and defines the private authentication state shared between SMB client/server session setup and the implementation in `krb5-wrapper.c`.

## Important APIs, Types, and Functions
The key type is `struct private_auth_data`, which contains GSS context and credential handles, user and target names, mechanism selection, request flags, current output token, proxy/SPNEGO flags, a service-name string, krb5 context/cache/principal/keytab handles, and stored server credentials. The header declares token accessors, client negotiation/session functions, server credential/session functions, GSS error formatting, NTLMSSP capability probing, and cleanup helpers.

## Control Flow
There is no runtime control flow in the header. Preprocessor guards expose all declarations only when `HAVE_LIBKRB5` is defined. Non-Apple builds include `gssapi_ext.h` and define a SPNEGO OID; all builds define Kerberos and NTLMSSP mechanism OID descriptors used by the implementation to constrain or detect mechanisms.

## State and Persistence Behavior
The header defines ownership-bearing fields but does not allocate them. The implementation is responsible for releasing GSS buffers, names, contexts, creds, krb5 ccaches, keytabs, principals, and `g_server`. Because the struct is private to the libsmb2 build rather than a stable public ABI, field changes must be coordinated with all internal users.

## Dependencies and Integration Points
It depends on `config.h`, `krb5/krb5.h`, Apple `GSS/GSS.h` or standard `gssapi.h`/`gssapi_ext.h`, and forward declarations for `struct smb2_context`/`struct smb2_server` from included SMB headers in translation units. It is the contract between SMB session setup code and Kerberos support.

## Risks and Edge Cases
The header exposes `static const gss_OID_desc` objects in every including translation unit, which is fine for internal use but means pointer identity is per translation unit. Some prototypes reference `struct smb2_context` and `struct smb2_server` without declaring them locally, so include order must provide those types. The declared `krb5_negotiate_request()` is not implemented in the inspected `krb5-wrapper.c`, suggesting either a stale prototype or an implementation elsewhere that should be verified during link tests.

## Test Signals
Compile coverage should include `HAVE_LIBKRB5` on/off, Apple and non-Apple GSS headers, C++ inclusion, and link checks for every declared function. Runtime tests are driven through `krb5-wrapper.c`: token accessors, cleanup ownership, mechanism selection, server credential initialization, and NTLMSSP capability probing.
