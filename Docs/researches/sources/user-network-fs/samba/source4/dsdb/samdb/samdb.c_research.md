# sources/user-network-fs/samba/source4/dsdb/samdb/samdb.c

## Purpose
`samdb.c` provides core SAM database connection helpers and AD security-token construction.

## Important APIs, Types, and Functions
`samdb_connect_url` connects to a SAM LDB URL with Samba wrappers, optional shared-context caching, global schema setup, and optional remote-address opaque state. `samdb_connect` is the `sam.ldb` convenience wrapper. `security_token_create` constructs a `security_token` from user SIDs, device SIDs, claims, session flags, and privilege policy.

## Control Flow and Behavior
`samdb_connect_url` always sets `LDB_FLG_DONT_CREATE_DB`, first attempts to reuse a cached wrapper when no remote address is supplied, then initializes and connects a new Samba LDB context. Remote-address connections are deliberately not added to the wrapper cache so audit/netlogon state remains per connection. The `SAMBA_LDB_WRAP_CONNECT_FLAG_NO_SHARE_CONTEXT` flag also bypasses cache insertion.

`security_token_create` initializes a token with claims-evaluation mode derived from loadparm, deduplicates user SIDs, tracks whether claims are valid and whether authentication is compounded, optionally deduplicates device SIDs, assigns simple privileges from well-known token class when requested, otherwise loads privileges from `privilege.ldb`, converts claims only when the Claims Valid SIDs are present, and emits token debug output.

## State and Persistence Behavior
Connection state may be shared through `ldb_wrap_find`/`ldb_wrap_add` unless remote address or no-share flags force uniqueness. `samdb_connect_url` sets the global schema for the context before connecting. Security tokens are in-memory state owned by the caller's talloc context; privilege data is read from persistent `privilege.ldb` through `samdb_privilege_setup`.

## Dependencies and Integration Points
The file integrates with `samba_ldb_init`, `samba_ldb_connect`, LDB wrapper caching, loadparm, auth session info, tsocket addresses, security SID helpers, claims conversion, local privilege setup, and generated SAMDB prototypes. It is central to AD DC code that needs a SAM LDB context or a fully populated access token.

## Risks and Edge Cases
Connection caching is intentionally disabled for remote-address-aware callers; accidentally passing NULL remote address can collapse distinct client contexts. The over-allocation comment in `security_token_create` is followed by immediate realloc growth during deduplication, so allocation behavior depends on realloc success. Device SIDs are considered only for compounded authentication. Claims are ignored unless the corresponding Claims Valid SID is present. Missing privilege DB access fails token creation unless simple privileges were requested.

## Test Signals
Coverage should include cached and uncached SAM DB connections, remote-address opaque storage, no-share flag behavior, connection error string paths, SID deduplication, system/anonymous/builtin-administrator simple privileges, privilege DB failure handling, compounded device SID handling, Claims Valid SID gating, and loadparm-controlled claims evaluation.
