# sources/user-network-fs/samba/source3/include/smb_krb5.h

## Purpose
`smb_krb5.h` is a very small aggregator header for Samba's Kerberos and GSSAPI wrapper interfaces in source3.

## Important APIs, Types, and Functions
The header directly includes:
- `lib/krb5_wrap/krb5_samba.h`
- `lib/krb5_wrap/gss_samba.h`

It declares no local functions, types, constants, or include guard of its own.

## Control Flow and State
There is no local control flow or state. Including this file makes the Kerberos/GSS wrapper APIs visible to code that historically expected `smb_krb5.h`.

## Persistence Behavior
No persistence is performed here. Kerberos credential caches, keytabs, and GSS state are managed by the included wrapper APIs and their implementations.

## Dependencies and Integration Points
This is a compatibility/convenience integration point for authentication and session setup code needing Samba's Kerberos and GSS wrappers. It relies entirely on the wrapped library headers for platform abstraction.

## Risks
- Because it lacks a local guard, repeated inclusion safety depends on the included wrapper headers.
- Any change to this file can have broad build impact in authentication-related source3 code that includes it transitively.

## Test Signals
Compile coverage for Kerberos-enabled and Kerberos-disabled builds is the main signal. Authentication tests using SPNEGO/GSS/Kerberos validate the real downstream behavior.
