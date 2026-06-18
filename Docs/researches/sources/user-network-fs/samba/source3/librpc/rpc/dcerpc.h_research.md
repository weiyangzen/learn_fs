# sources/user-network-fs/samba/source3/librpc/rpc/dcerpc.h

## Purpose
`dcerpc.h` is a public source3 DCERPC helper header. It exposes helper APIs for packet encoding, auth trailer encoding, fragment sizing, auth footer creation, and auth verification.

## Important APIs, types, and functions
- `dcerpc_push_ncacn_packet()` encodes an `ncacn_packet`.
- `dcerpc_push_dcerpc_auth()` encodes a `dcerpc_auth` trailer header.
- `dcerpc_guess_sizes()` computes data, fragment, auth, and padding lengths for a fragment.
- `dcerpc_add_auth_footer()` appends auth padding/trailer/signature or seal data.
- `dcerpc_check_auth()` validates and possibly decrypts an incoming packet trailer.

## Control flow
The header declares the flow implemented in `dcerpc_helpers.c`: callers build packet payloads, estimate fragment sizes, append auth footers before transmission, and check incoming auth after NDR parsing.

## State and persistence behavior
No state is stored here. The APIs operate on `pipe_auth_data`, blobs, packets, and GENSEC contexts owned elsewhere.

## Dependencies and integration points
The header includes generated DCERPC NDR definitions, libndr, and common RPC types. It forward-declares `struct gensec_security` and `struct pipe_auth_data`. It is noted as a public installed header, so signature changes affect Samba ABI/SO versioning.

## Risks and edge cases
Because this is public, removing or changing function signatures requires SO-version review. Callers must obey size and ownership contracts for blobs and packet trailers.

## Test signals
Compile external/internal consumers, run DCERPC fragment/auth tests, and include ABI checks for exported signatures.
