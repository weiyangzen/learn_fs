# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ActorFuzz.h

## Purpose
`ActorFuzz.h` declares the interface between generated actor fuzz tests and the Flow actor DSL test harness.

## Important APIs, Types, and Functions
It defines inline `throw_operation_failed`, declares `testFuzzActor` with a signature adjusted for `OPEN_FOR_IDE`, and declares `actorFuzzTests()` returning passed and total counts.

## Control Flow
The header has no runtime control flow except `throw_operation_failed`, which throws `operation_failed()`. Generated actors include this helper to test actor compiler handling of throwing callees.

## State and Persistence Behavior
There is no persistent or mutable state.

## Dependencies and Integration Points
It depends on `flow/flow.h` and `std::vector`. `actorFuzz.py` generates a source file that includes this header, and `dsltest.actor.cpp` implements `testFuzzActor` and calls `actorFuzzTests()`.

## Risks and Edge Cases
The IDE signature differs from the compiled signature because actor compiler transformations handle references differently. Consumers must keep generated actor signatures aligned with this header and `dsltest.actor.cpp`.

## Test Signals
Successful compilation of generated `ActorFuzz.actor.cpp` and correct `actorFuzzTests()` pass counts are the direct signals.
