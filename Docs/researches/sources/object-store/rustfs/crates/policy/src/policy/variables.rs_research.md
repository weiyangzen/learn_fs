# sources/object-store/rustfs/crates/policy/src/policy/variables.rs

## Purpose

Implements AWS-style policy variable resolution for resources and string conditions. It supports request-derived variables, claim-derived variables, custom variables, dynamic time variables, multi-value expansion, nested variable resolution, and optional caching for non-dynamic variables.

## Important APIs, Types, and Functions

- `VariableContext` carries HTTPS flag, source IP, account ID, region, username, claims, request conditions, and custom variables.
- `VariableResolverCache` wraps a `moka::future::Cache<String, String>`.
- `CachedAwsVariableResolver` delegates to `VariableResolver` and caches non-dynamic single-value resolutions for five minutes by default.
- `PolicyVariableResolver` is the async trait with `resolve`, `resolve_multiple`, and `is_dynamic`.
- `VariableResolver` resolves AWS variables from `VariableContext`.
- `resolve_aws_variables(pattern, resolver)` expands `${...}` placeholders into one or more strings, with up to ten iterative passes.
- `resolve_single_pass` finds variables, handles nested placeholders, expands multi-values by splicing multiple result strings, and leaves unknown variables unchanged.

## Control Flow

Variable resolution starts with the original pattern as a single result. Each pass calls `resolve_single_pass` on each current result. When a placeholder resolves to multiple values, the result list branches into one string per value. Duplicates are removed while preserving order. Resolution repeats until no changes occur or ten iterations are reached.

`VariableResolver` maps `aws:username` to context username, `aws:userid` to `sub` or `parent` claim values, `aws:PrincipalType` to `AssumedRole`, `ServiceAccount`, or `User`, `aws:SecureTransport` to a boolean string, current/epoch time to UTC time values, and account/region/source IP/custom variables from context. `resolve_multiple` supports multi-value `aws:userid` from array claims.

Nested variables such as `${${aws:PrincipalType}-${aws:userid}}` first resolve the inner expression to a variable name, then a later pass can resolve that generated variable if a resolver supplies it.

## State and Persistence

The base resolver holds an owned `VariableContext`. The cached resolver has an in-memory moka cache with capacity and TTL. Dynamic variables (`aws:CurrentTime`, `aws:EpochTime`) bypass the cache.

## Dependencies and Integration Points

Used by `Statement::variable_resolver_for_policy_args`, `Resource::is_match_with_resolver`, and string condition evaluation. Depends on `async_trait`, `moka`, `serde_json::Value`, `time::OffsetDateTime`, and async futures for recursive resolution.

## Risks and Edge Cases

- The ten-iteration cap prevents infinite recursion but may leave deeply nested or cyclic variables partially unresolved.
- Unknown variables remain as placeholders, so patterns can fail to match silently rather than error.
- `resolve_userid` uses `pop()` for single resolution, meaning arrays return the last element in single-value contexts; multi-value resolution returns all values.
- Cache keys are only variable names, so cached values are safe only because each cache instance is tied to one context.
- `conditions` exists in `VariableContext` but is not directly used by `VariableResolver` in this file; common condition substitution happens in string/resource matchers.

## Test Signals

Inline tests cover username, userid, multiple variables, no-variable pass-through, Unicode prefix preservation, and dynamic variables bypassing cache by comparing epoch-time resolutions across a delay. Policy-level tests cover nested and multi-value expansion.
