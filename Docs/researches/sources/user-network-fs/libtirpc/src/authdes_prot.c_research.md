<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/authdes_prot.c -->
# sources/user-network-fs/libtirpc/src/authdes_prot.c

Purpose: XDR serialization routines for AUTH_DES credential and verifier structures.

Important APIs, types, and functions: Exports `xdr_authdes_cred` and `xdr_authdes_verf`.

Control flow: Credential encoding first serializes the name-kind enum, then switches between full-name form (name, key, window) and nickname form. Verifier encoding serializes encrypted timestamp and integer union field.

State and persistence behavior: No retained state. XDR_DECODE may allocate strings through XDR helpers according to normal XDR ownership rules.

Dependencies and integration points: Used by `auth_des.c` marshal/validate and included with AUTH_DES support.

Risks: K&R-style definitions are legacy but valid in this codebase. Correct max lengths and opaque sizes are security-relevant because credentials cross trust boundaries.

Test signals: Compile coverage with AUTH_DES; no direct codec fixture in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/authdes_prot.c -->
