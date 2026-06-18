# sources/object-store/rustfs/crates/security-governance/src/redaction.rs

## Purpose
Defines redaction classifications and validates static redaction rule tables for fields that appear in logs, diagnostics, admin output, or configuration surfaces.

## Important APIs and Types
`RedactionLevel` has `Public`, `Sensitive`, and `Secret`; helpers `requires_redaction` and `is_secret` encode policy semantics. `RedactionRule` stores a static field name, level, and reason with const constructor/getters. `RedactionPolicyError` reports empty field, empty reason, and duplicate field. `validate_redaction_rules` checks trimmed field/reason strings and uses a `BTreeSet<&'static str>` to enforce one rule per field.

## Control Flow and State
Validation is deterministic and side-effect free. There is no persistence or runtime registry; callers pass the policy table each time.

## Integration Points
Re-exported from the crate root, this module can be consumed by admin APIs, audit logging, diagnostics, or config serializers to assert that sensitive fields have explicit redaction metadata.

## Risks
Field identity is exact and case-sensitive, with no namespace awareness. The validator checks the existence and uniqueness of a rule but does not apply redaction itself. It also allows `Public` rules with arbitrary reasons, so enforcement depends on consumers respecting `RedactionLevel`.

## Test Signals
Unit tests cover valid public/secret rules and accessors, empty field, empty reason, and duplicate field rejection.
