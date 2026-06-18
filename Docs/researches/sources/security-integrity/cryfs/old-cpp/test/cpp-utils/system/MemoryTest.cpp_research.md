# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/MemoryTest.cpp

Purpose: Smoke-tests memory locking helpers with small and large allocation requests.

Important APIs and types: Uses `cpp-utils/system/memory.h`, standard smart pointers, compatibility helpers, and GoogleTest.

Control flow: Tests request locked memory regions or lock operations and assert they complete without crashing for small and large cases.

State and persistence behavior: Temporarily allocates/locks process memory. No persistent state.

Dependencies and integration points: Secure-memory or key-handling code may rely on these helpers to reduce swapping of sensitive data.

Risks: Actual lock success can depend on OS permissions and resource limits; these tests focus on no-crash behavior rather than guaranteed mlock.

Test signals: Locking calls complete without throwing/crashing for representative sizes.
