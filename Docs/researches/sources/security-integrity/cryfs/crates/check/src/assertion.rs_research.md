# sources/security-integrity/cryfs/crates/check/src/assertion.rs

Purpose: This module defines internal assertions that checks and the runner use to verify expected correlated errors are eventually reported. It is a self-checking mechanism for the checker algorithm, not a user-facing corruption type.

Important APIs and flow: `Assertion` has `ExactErrorWasReported(CorruptedError)` and `ErrorMatchingPredicateWasReported(Box<dyn Send + Fn(&CorruptedError) -> bool>, Location)`. Constructors build exact or predicate assertions; `validate` scans the final reported errors and panics if an expected error is absent.

State and persistence: Assertions live in `CheckResult` until finalization. They are in-memory consistency checks that tie partial observations, such as unreadable blobs or duplicate references, to final diagnostic output.

Dependencies and integration: The module depends on `CorruptedError` and `std::panic::Location`. `AllChecks`, `CheckParentPointers`, `CheckUnreferencedNodes`, and the runner add assertions for cases where one subsystem should detect an error discovered indirectly by another.

Risks and test signals: Failed assertions panic, which is appropriate for algorithm invariant violations but not graceful for end users if an edge case is missed. Predicate assertions preserve caller locations, improving debugging of checker implementation defects.
