# sources/object-store/rustfs/crates/security-governance/src/lib.rs

## Purpose
Crate root for `rustfs-security-governance`. It exposes four policy modules: `admin_matrix`, `redaction`, `serde_policy`, and `supply_chain`.

## Important APIs
The root re-exports all public contract types and validators: admin route specs and validation, redaction rules and validation, serde unknown-field policy validation, and artifact integrity policy validation. This creates a compact public surface for downstream governance checks.

## Control Flow, State, and Integration
No code executes here beyond module declaration and re-export. The design keeps downstream crates from depending on individual module paths and provides a stable facade.

## Risks and Test Signals
Risk is API compatibility: changing re-exports can break downstream crates even if module internals remain. Tests are in the module files rather than the root.
