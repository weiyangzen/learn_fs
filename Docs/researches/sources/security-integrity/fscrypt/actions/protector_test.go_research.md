# sources/security-integrity/fscrypt/actions/protector_test.go

## Purpose
Tests basic protector creation and callback error propagation.

## APIs and Control Flow
Defines shared constants, a callback error, `goodCallback` returning a fixed-length key from `timingPassphrase`, and `badCallback` returning `errCallback`. `TestCreateProtector` creates, locks, and destroys a protector. `TestBadCallback` verifies `CreateProtector` returns the original callback error and does not require cleanup if creation failed.

## State, Dependencies, and Integration
Uses the shared integration `testContext` and real metadata persistence. The `goodCallback` is also reused by policy and recovery tests.

## Risks and Test Signals
Coverage is narrow but protects the important guarantee that key callbacks are not swallowed or converted. More source-specific protector behavior is covered in CLI tests.
