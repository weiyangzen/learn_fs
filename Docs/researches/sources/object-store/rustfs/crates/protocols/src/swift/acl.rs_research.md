# sources/object-store/rustfs/crates/protocols/src/swift/acl.rs

## Purpose
This file models and evaluates Swift container ACLs. It parses `X-Container-Read` and `X-Container-Write` header values into typed grants, serializes grants back to headers, and checks whether a request account/user/referrer is allowed. It intentionally allows public/referrer grants only for read ACLs and rejects public write ACLs.

## Important APIs, Types, And Functions
- `ContainerAcl { read, write }` stores parsed read and write grants.
- `AclGrant` represents `PublicRead`, `PublicReadReferrer(pattern)`, account-wide access, and user-specific access.
- `impl Display for AclGrant` serializes grants back to Swift header grammar.
- `ContainerAcl::parse_read` and `parse_write` split comma-separated headers, trim whitespace, and call `parse_grant`.
- `parse_grant(grant_str, allow_public)` recognizes `.r:*`, `.r:<pattern>`, `AUTH_account`, and `AUTH_account:user`.
- `check_read_access(request_account, request_user, referrer)` evaluates read grants and defaults empty read ACLs to authenticated access.
- `check_write_access(request_account, request_user)` evaluates write grants and defaults empty write ACLs to owner/caller write access.
- `matches_referrer_pattern` implements exact referrer matching plus leading-asterisk suffix matching.
- `read_to_header`, `write_to_header`, and `is_public_read` expose serialization and public-read inspection helpers.

## Control Flow
Parsing trims the whole header, returns an empty vector for empty values, then parses each non-empty comma-separated token. `.r:` grants are accepted only when parsing read ACLs; `.r:*` becomes public read and any other non-empty `.r:` suffix becomes a referrer pattern. `AUTH_` strings with a colon become user grants if the user part is non-empty; `AUTH_` strings without a colon become account grants. Any other string returns `BadRequest`.

Read access checks short-circuit on the first matching grant. Public read grants allow all callers. Referrer grants require a present `Referer` value matching exact or suffix pattern. Account and user grants require matching authenticated account and optionally user. Empty read ACLs allow any authenticated account and deny anonymous access.

Write access similarly scans write grants. Public grants are ignored defensively because parsing should prevent them. Account grants match the request account; user grants require both account and user. Empty write ACLs return true for the supplied request account, relying on callers to pass only the container owner or an otherwise authorized account.

## State And Persistence Behavior
This file is pure in-memory parsing and evaluation. It does not read or write storage itself. Persistence is handled by `container.rs`, which stores read/write ACL header strings in bucket tags named `swift-acl-read` and `swift-acl-write`, then reparses them through this module on retrieval.

## Dependencies And Integration Points
The module uses the local `SwiftError`/`SwiftResult` type and `tracing::debug` for structured ACL decision logs. It integrates with `container::set_container_acl` and `container::get_container_acl`, and likely with Swift object/container handlers that need to enforce public or cross-account access.

## Risks And Edge Cases
- Referrer matching is simple suffix matching for patterns starting with `*`; it does not parse URLs or normalize scheme/host. A full URL referrer may not match patterns as operators expect, or may match by suffix in surprising ways.
- Empty read ACLs allow any authenticated account according to this function, while comments say "owner can read". Correct ownership enforcement must happen before or around this check.
- Empty write ACLs return true for any supplied `request_account`, again relying on caller-side owner scoping.
- The parser accepts account names beginning `AUTH_` without validating project id shape.
- Duplicate grants are preserved and serialized; no normalization or deduplication is performed.
- Public write is rejected at parse time, but if a malformed `ContainerAcl` is constructed manually with public grants in `write`, they are silently ignored.

## Test Signals
The test module is broad. It covers parsing public, referrer, account, user, mixed, empty, and invalid ACLs; rejection of public write ACLs; read/write access decisions for public, referrer, account, and user grants; default empty ACL behavior; serialization; public-read detection; whitespace handling; multiple referrer patterns; user-specific requirements; ACL removal; and complex read/write scenarios. There are no persistence tests in this file because storage is delegated to `container.rs`.
