# sources/sync-backup/kopia/repo/format/format_blob_key_derivation_testing.go

## Purpose
Defines test-build defaults for format encryption key derivation, replacing production Scrypt with an insecure fast algorithm to speed tests.

## Important APIs, Types, And Functions
Under `testing`, `DefaultKeyDerivationAlgorithm` is `crypto.TestingOnlyInsecurePBKeyDerivationAlgorithm`.

## Control Flow
No functions are defined in this file.

## State And Persistence
When built with the `testing` tag, new test repositories persist the insecure KDF name unless explicitly overridden.

## Dependencies And Integration Points
Depends on `internal/crypto` and is consumed by `format.Initialize` through the shared constant name.

## Risks And Edge Cases
This file must never be used in production builds; the build tag separation is the safety boundary. It intentionally changes security/performance behavior for tests.

## Test Signals
Format manager and upgrade tests indirectly rely on this faster default under test builds.
