# sources/object-store/garage/src/model/admin_token_table.rs

## Purpose
This file defines the replicated metadata table for Garage admin API bearer tokens. It stores token identifiers, argon2 password hashes of the full token, human-visible names, optional expiration, and endpoint scopes in CRDT-friendly structures so admin credentials can be created, updated, revoked, filtered, and replicated through the control-plane table system.

## Important APIs, types, and functions
`AdminApiToken` stores the public token prefix and a `crdt::Deletable<AdminApiTokenParams>`. `AdminApiTokenParams` contains `created`, `token_hash`, LWW `name`, LWW optional `ExpirationTime`, and LWW `AdminApiTokenScope`. `AdminApiTokenScope` wraps a vector of endpoint/scope strings. `AdminApiToken::new` generates `<prefix>.<secret>`, hashes the full bearer token with Argon2 and a random salt, and returns both the persisted record and plaintext token. `delete`, `is_deleted`, `params`, `params_mut`, `scope`, `is_expired`, and `has_scope` are the main accessors and policy checks. `AdminApiTokenTable` implements `TableSchema` under `admin_token` and reuses `KeyFilter` for deleted and name/prefix search.

## Control flow
Creation generates a random 12-byte hex prefix and a 32-byte URL-safe base64 secret, hashes the joined token, and initializes scope to `["*"]`. Normal admin authentication paths can look up by prefix, verify the plaintext token against `token_hash` elsewhere, then call `is_expired` and `has_scope`. Table filtering lowercases the search pattern and matches non-deleted token prefixes or exact lowercased names.

## State and persistence behavior
Only the token prefix and password hash are persisted; the plaintext bearer token is returned once from `new`. The table has an explicit migration marker `G2admtok`. Mutable fields are CRDTs: name, expiration, and scope are LWW values, while delete state uses `Deletable`. Scope merge is restrictive intersection, so concurrent divergent scope edits converge to the common allowed endpoints.

## Dependencies and integration points
The table depends on `garage_util::crdt`, `garage_table::{Entry, TableSchema}`, `garage_util::time::now_msec`, `base64`, `rand`, `hex`, and `argon2`. It is instantiated by `Garage::new` as a fully replicated control table and exposed to admin API logic. `ExpirationTime` comes from `permission.rs`; filters come from `key_table.rs`.

## Risks and edge cases
Plaintext tokens are only available at creation, so callers must surface them immediately. `AdminApiTokenScope::merge` computes intersection but preserves the left-side ordering and duplicates if present, so API-side validation should normalize scopes. Argon2 failures panic via `expect`, which is acceptable for normal randomness/hash configuration but not recoverable. Search matches names by exact lowercase equality, not substring. Expiration timestamps must use the same millisecond timebase as `now_msec`.

## Test signals
There are no direct tests in this file. The `arbitrary` feature can generate token scopes for fuzz/property tests. Meaningful coverage should exercise create/verify/revoke flows, scope intersection under concurrent edits, expiration boundary checks, and table filtering.
