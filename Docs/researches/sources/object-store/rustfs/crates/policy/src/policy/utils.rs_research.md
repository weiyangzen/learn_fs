# sources/object-store/rustfs/crates/policy/src/policy/utils.rs

## Purpose

Provides shared policy utility modules and small helper functions for claim lookup and policy database path splitting.

## Important APIs, Types, and Functions

- Re-exports submodules `path` and `wildcard`.
- `ClaimLookup<'a>` distinguishes missing claims, a found claim value, and ambiguous case-insensitive matches.
- `get_claim_case_insensitive(claims, claim_name)` prefers exact key matches and otherwise finds a single Unicode-aware case-folded match.
- `_get_values_from_claims(claim, chaim_name)` parses exact-name string or array claims into comma-split values.
- `_split_path(path, second_index)` splits a path after the first slash or second slash depending on storage layout.

## Control Flow

Case-insensitive lookup first checks `HashMap::get` for exact match. If absent, it scans every claim key using `case_insensitive_eq`, which lowercases chars without allocating entire strings. The first folded match is retained; a second folded match returns `Ambiguous`. Path splitting finds either the first slash or, when `second_index` is true, the second slash, then returns the prefix including slash and the rest.

## State and Persistence

No state or persistence. Helpers operate on caller-supplied maps and strings.

## Dependencies and Integration Points

Used by policy claim extraction in `policy.rs` and any IAM storage code needing path splitting. `path` and `wildcard` submodules are used by resource and principal matching.

## Risks and Edge Cases

- `_get_values_from_claims` uses exact key lookup only and appears superseded by case-insensitive helpers for policy claims.
- `case_insensitive_eq` is Unicode-aware through `char::to_lowercase`, but not full locale-specific collation.
- Ambiguous folded claims are treated as missing by callers, reducing confused-deputy risk at the cost of ignoring potentially valid claims.
- `_split_path` returns the whole path and empty rest if the expected slash is absent.

## Test Signals

Inline tests cover path splitting for normal user/group/policydb layouts, slash-containing LDAP-like names, exact-match preference, ambiguity detection, and Unicode case matching.
