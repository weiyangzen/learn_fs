<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy.rs -->
# sources/object-store/rustfs/crates/policy/src/policy.rs

Purpose: Top-level policy module facade. It declares policy submodules, re-exports core policy types, and defines policy-syntax validation errors.

Important APIs/types/functions: Public/re-exported API includes `ActionSet`, `PolicyDoc`, `Effect`, `Functions`, `ID`, `Policy`, `Principal`, `ResourceSet`, `Statement`, `ClaimLookup`, and `get_claim_case_insensitive`. Submodules include action, doc, effect, function, id, opa, policy, principal, resource, statement, utils, and variables. `policy::Error` variants describe invalid policy version/effect/action/key/resource shape and conflicting action/resource fields.

Control flow: This file has no evaluator logic itself; it centralizes module wiring and the error taxonomy used by validators and deserializers in submodules.

State/persistence behavior: None directly. Re-exported types define persisted policy documents and evaluation state.

Dependencies/integration: The outer crate `error::Error` wraps `policy::Error`, and downstream code imports policy primitives from here. `opa`, `resource`, `statement`, and `variables` are part of the broader policy engine even though this work item focuses on specific files.

Risks/test signals: Re-export choices define API stability. `function` is private but `Functions` is public, so internals can change while the condition aggregate stays exposed. No tests in this file directly; submodule tests cover individual behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy.rs -->
