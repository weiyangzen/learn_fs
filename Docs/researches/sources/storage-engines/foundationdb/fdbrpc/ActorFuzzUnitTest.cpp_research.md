# sources/storage-engines/foundationdb/fdbrpc/ActorFuzzUnitTest.cpp

Purpose: small unit-test bridge that links the generated actor fuzz corpus into the Flow/FoundationDB unit-test framework.

Important APIs and functions: `forceLinkActorFuzzUnitTests()` is an empty symbol used to force linker inclusion. `TEST_CASE("/actorFuzz")` calls `actorFuzzTests()` and asserts all generated tests passed.

Control flow: the test receives a `{passed, total}` pair and asserts equality. It returns `Void()` for the actor-based unit-test runner.

State and persistence behavior: no persistent state. Test state is contained in generated actor executions and expected marker comparisons.

Dependencies and integration points: includes `fdbrpc/ActorFuzz.h` and `flow/UnitTest.h`. It depends on `ActorFuzz.actor.cpp` for `actorFuzzTests`.

Risks: if the generated corpus is not linked, this file is the intended anchor, but build-system changes can still affect inclusion. It reports only aggregate equality, so detailed failure information comes from lower-level `testFuzzActor`.

Test signals: clear pass/fail gate for all actor fuzz generated cases.
