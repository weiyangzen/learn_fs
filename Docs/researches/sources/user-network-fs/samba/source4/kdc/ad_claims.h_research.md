# sources/user-network-fs/samba/source4/kdc/ad_claims.h

## Purpose

`ad_claims.h` declares the KDC-facing Active Directory claims utility interface used to decide whether to issue claims and to build a claims set for a principal.

## Important APIs, Types, and Functions

The header forward-declares `struct CLAIMS_SET` and declares `ad_claims_are_issued(struct ldb_context *samdb)` plus `get_claims_set_for_principal(struct ldb_context *ldb, TALLOC_CTX *mem_ctx, const struct ldb_message *principal, struct CLAIMS_SET **claims_set_out)`. It includes `data_blob.h` and `ldb.h` for shared Samba/LDB types.

## Control Flow

There is no runtime control flow in the header. Callers first may use `ad_claims_are_issued()` as a feature gate, then call `get_claims_set_for_principal()` with an LDB principal message containing at least `objectClass`.

## State and Persistence Behavior

The API returns claim data allocated under the caller's talloc context. `claims_set_out` is set to `NULL` when claims are not issued or no configured claims produce values. The header itself owns no state.

## Dependencies and Integration Points

This is the integration point between KDC PAC code and `ad_claims.c`. Consumers must link against the KDC claims implementation and generated claims NDR types even though the header keeps `CLAIMS_SET` opaque.

## Risks and Edge Cases

Callers must provide a sufficiently populated principal message; missing `objectClass` causes an operational error in the implementation. The returned `CLAIMS_SET` lifetime follows `mem_ctx`, so PAC assembly must not outlive that context.

## Test Signals

Compile coverage validates signature consistency. Runtime coverage should confirm callers handle `NULL` claim sets and LDB error returns distinctly.
