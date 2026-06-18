# sources/object-store/rustfs/crates/security-governance/src/serde_policy.rs

## Purpose
Defines governance rules for serde unknown-field handling. It lets the project declare whether a target schema is strict ingress, tolerant compatibility, or persistent legacy data, and validates that the unknown-field policy matches that role.

## Important APIs and Types
`UnknownFieldPolicy` is `Deny`, `Warn`, or `Preserve`. `SerdePolicyKind` is `StrictIngress`, `TolerantCompat`, or `PersistentLegacy`. `SerdePolicy` stores a static target, kind, and unknown-field policy with const constructor/getters. `SerdePolicyError` reports empty target, strict ingress not denying unknown fields, compatibility/legacy policy denying unknown fields, and duplicate target.

`validate_serde_policies` checks non-empty targets, then enforces kind/policy combinations: strict ingress must deny; tolerant compatibility and persistent legacy must not deny. A `BTreeSet` enforces one policy per target.

## Control Flow and State
The module has no runtime state. Validation is a simple ordered scan that returns the first detected policy error.

## Integration Points
This module supports code or CI checks around JSON/XML/config DTOs. It is re-exported from `lib.rs` for consumers that need to document or enforce serde compatibility posture.

## Risks
The policy table is advisory unless wired into actual serde attributes or test gates. Target matching is exact and unqualified. There is no severity level for `Warn`, and no way to express mixed behavior within a single target.

## Test Signals
Unit tests validate strict, legacy, and tolerant examples and reject empty targets, strict ingress without `Deny`, compat/legacy with `Deny`, and duplicate targets.
