# sources/user-network-fs/libnfs/lib/krb5-wrapper.h

## Purpose
Header for optional libnfs Kerberos/GSSAPI authentication support.

## Important APIs, Types, And Functions
- Defines SPNEGO/Kerberos mechanism OIDs, with Apple-specific GSS imports.
- Defines `struct private_auth_data` containing GSS context, credentials, names, chosen mechanism, request flags, output token, server string, and wanted security mode.
- Declares auth initialization, request, cleanup, GSS error formatting, and token accessors.

## Control Flow
No executable flow. All content is gated by `HAVE_LIBKRB5`, so consumers compile without declarations when Kerberos support is absent.

## State And Persistence
No state in the header. The struct describes per-RPC-context authentication state owned by the implementation.

## Dependencies And Integration Points
Included by `init.c` and `krb5-wrapper.c`; requires `struct rpc_context` to be visible to callers via libnfs private headers.

## Risks
Static OID descriptors in a header give each translation unit private copies, which is acceptable but should remain intentional. The API is unavailable entirely without `HAVE_LIBKRB5`, so call sites must be guarded.

## Test Signals
Compile C and C++ consumers with Kerberos enabled, disabled, Apple GSS, and non-Apple GSS; validate struct fields match implementation expectations.
