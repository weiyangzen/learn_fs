# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/testutils/FakeAuthenticatedCipher.cpp

## Purpose
Provides a deterministic fake authenticated cipher for tests that need cipher-like behavior without relying on real cryptographic transformations. This specific file has 8 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/testutils` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `FakeAuthenticatedCipher.h`.

## Control Flow
The fake cipher derives deterministic output from the fake key and payload sizes, appends/checks an authentication marker, and exposes the same static API shape as real ciphers for concept-based tests.

## State and Persistence Behavior
The fake cipher keeps no global state; deterministic fake keys and serialized test payloads are created in memory.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `FakeAuthenticatedCipher.h`.

## Risks and Edge Cases
The fake cipher is intentionally not secure and must remain test-only. Accidentally linking it into production paths would invalidate crypto guarantees.

## Test Signals
Use it only in tests that verify authentication-failure plumbing, serialization sizes, and deterministic fake key behavior.
