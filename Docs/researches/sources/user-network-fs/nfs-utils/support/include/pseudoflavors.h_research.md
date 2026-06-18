# sources/user-network-fs/nfs-utils/support/include/pseudoflavors.h

## Purpose
Defines RPCSEC_GSS pseudoflavor numbers and the security flavor lookup table contract.

## Important APIs, Types, and Functions
`RPC_AUTH_GSS_KRB5*` constants, `struct flav_info`, extern `flav_map[]`, and `flav_map_size`.

## Control Flow
Export option parsing and pseudo-root security setup iterate `flav_map`, check flavor numbers and krb5 requirements, then add secinfo entries.

## State and Persistence Behavior
No state here besides extern table declarations. Security choices can persist in export entries and kernel cache replies.

## Dependencies and Integration Points
Used by `v4root.c`, export option parsing, and secinfo serialization.

## Risks and Edge Cases
Numbers must match kernel/RPCSEC_GSS assignments. `need_krb5` behavior depends on local keytab checks in consumers.

## Test Signals
Test flavor parsing, secinfo output for krb5/krb5i/krb5p, and pseudo-root behavior with and without keytab.
