# sources/user-network-fs/samba/source3/librpc/crypto/gse.h

## Purpose
`gse.h` is the small public header for source3's GSSAPI Security Extensions backend. It forward-declares the private context and exposes the mechanism lookup function used by generic authentication setup.

## Important APIs, types, and functions
- `struct gse_context` is intentionally opaque to users outside `gse.c`.
- `gensec_gse_security_by_oid(const char *oid_string)` returns a `gensec_security_ops` table for supported GSE mechanisms.

## Control flow
There is no executable control flow in this header. Its role is compile-time linkage: callers include it, pass an OID, and receive a GENSEC ops pointer when Kerberos GSE is available.

## State and persistence behavior
No state is declared beyond the opaque context type. All context allocation, credential lifecycle, and persistence effects remain hidden in `gse.c` and `gse_krb5.c`.

## Dependencies and integration points
The header relies on declarations of `struct gensec_security_ops` from GENSEC include chains. It is included by code that registers or selects authentication backends, notably `libsmb/auth_generic.c`, and by DCERPC helpers indirectly through GENSEC.

## Risks and edge cases
The API exposes only OID-based lookup. Callers must handle `NULL` returns for unsupported OIDs or builds without Kerberos support. Because the header hides `struct gse_context`, ABI risk is low, but the function signature is a stable integration point.

## Test signals
Build tests should verify both Kerberos-enabled and Kerberos-disabled configurations. Runtime tests should confirm callers correctly skip GSE when lookup returns `NULL`.
