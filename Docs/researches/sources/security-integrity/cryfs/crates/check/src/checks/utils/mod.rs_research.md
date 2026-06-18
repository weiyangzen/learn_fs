# sources/security-integrity/cryfs/crates/check/src/checks/utils/mod.rs

Purpose: This module exposes utility helpers for checks.

Important APIs and flow: It currently declares only `pub mod reference_checker;`, making the generic reference tracking helper available to sibling check modules.

State and persistence: It owns no state. State lives in `reference_checker.rs` instances.

Dependencies and integration: It is imported by `checks::parent_pointers` and `checks::unreferenced_nodes` through `super::utils::reference_checker::ReferenceChecker`.

Risks and test signals: The module is intentionally minimal. Any future utility exports should remain generic enough to avoid coupling check implementations unnecessarily.
