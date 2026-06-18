# sources/user-network-fs/samba/source3/librpc/rpc/dcerpc_internal.h

## Purpose
`dcerpc_internal.h` defines source3 internal DCERPC authentication state shared by helper and transport code.

## Important APIs, types, and functions
- `struct pipe_auth_data` stores auth type, auth level, auth context ID, header-signing and verification flags, and the active `gensec_security *auth_ctx`.

## Control flow
There is no executable flow. Transport code populates `pipe_auth_data`; `dcerpc_helpers.c` reads it to size fragments, add auth footers, and validate incoming packets.

## State and persistence behavior
The structure is runtime connection/pipe state only. It references a live GENSEC context and should not be serialized as-is.

## Dependencies and integration points
It depends on generated DCERPC auth enum types and GENSEC forward declarations. The fields align with DCERPC bind/auth negotiation and packet protection helpers.

## Risks and edge cases
`auth_type`, `auth_level`, and `auth_context_id` must match the negotiated bind state and incoming trailers. `hdr_signing` and `verified_bitmask1` are subtle protocol flags; inconsistent use can weaken header integrity checks. `auth_ctx` must outlive helper calls.

## Test signals
Exercise negotiated auth state across bind, alter context, request, and response flows, including context ID mismatches and header-signing-required cases.
