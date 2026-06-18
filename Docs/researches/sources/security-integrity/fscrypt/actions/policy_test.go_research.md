# sources/security-integrity/fscrypt/actions/policy_test.go

## Purpose
Integration tests for policy creation, modification, and unlock paths.

## APIs and Control Flow
`makeBoth` creates a protector and a policy using the shared `testContext`. Cleanup helpers lock and destroy objects. Tests validate creating a policy/protector pair, adding a second protector, rejecting duplicate protector attachment, removing an added protector, rejecting removal of absent or only protectors, unlocking by option callback, unlocking with an already-unlocked protector, and rejecting unlock with a locked protector.

## State, Dependencies, and Integration
All tests write real fscrypt metadata under the test mount and use the real crypto wrapping path. They depend on callback helpers from `protector_test.go` and fixture setup from `context_test.go`.

## Risks and Test Signals
The tests focus on metadata-level behavior, not kernel keyring provisioning or policy application to directories. They provide good regression coverage for wrapped-key list invariants and `ErrLocked` behavior.
