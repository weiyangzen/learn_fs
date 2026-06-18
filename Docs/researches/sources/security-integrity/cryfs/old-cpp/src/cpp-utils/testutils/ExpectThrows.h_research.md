# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/testutils/ExpectThrows.h

## Purpose
Provides test-only RAII and expectation helpers for capturing stderr and checking exception behavior. This specific file has 32 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/testutils` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Exception`, `Functor`. Macros/constants: `MESSMER_CPPUTILS_EXPECTTHROWS_H`. Important declarations or call sites include `inline void expectThrows(Functor&& functor, const char* expectMessageContains) {`; `std::forward<Functor>(functor)();`; `} catch (const Exception& e) {`; `EXPECT_THAT(e.what(), testing::HasSubstr(expectMessageContains));`; `inline void expectFailsAssertion(Functor&& functor, const char* expectMessageContains) {`; `expectThrows<cpputils::AssertFailed>(std::forward<Functor>(functor), expectMessageContains);`. CMake commands used here include `EXPECT_THAT`, `ADD_FAILURE`. Primary includes/dependencies visible in the file include `gmock/gmock.h`, `cpp-utils/assert/assert.h`.

## Control Flow
Test helpers wrap a scope around stderr redirection or exception assertions so tests can express expected failure behavior with minimal boilerplate.

## State and Persistence Behavior
State is scoped to a test and restored in destructors.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `gmock/gmock.h`, `cpp-utils/assert/assert.h`.

## Risks and Edge Cases
Test helpers can mask unexpected exceptions if predicates are too broad, and stderr capture must restore descriptors even on failure.

## Test Signals
Validate helper self-tests by capturing known stderr output and matching expected exception types/messages.
