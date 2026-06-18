# sources/storage-engines/leveldb/util/no_destructor_test.cc

## Purpose
Validates that `NoDestructor<T>` constructs the target object with forwarded arguments and never invokes the target destructor.

## Important APIs, Types, And Functions
The local `DoNotDestruct` struct stores two constructor arguments and calls `std::abort()` in its destructor. Tests construct `NoDestructor<DoNotDestruct>` with `kGoldenA` and `kGoldenB` and inspect fields through `get()`.

## Control Flow
`StackInstance` creates a wrapper as an automatic variable and exits the test scope; if the contained destructor ran, the process would abort. `StaticInstance` does the same for a function-local static wrapper, covering the intended singleton use case.

## State And Persistence Behavior
Only in-memory test objects are created. The static instance persists for process lifetime and is intentionally not destroyed at test shutdown.

## Dependencies And Integration Points
The file depends on GoogleTest and `util/no_destructor.h`. It indirectly confirms compatibility with primitive constructor arguments, static storage, and stack storage.

## Risks And Edge Cases
The test does not cover non-trivial alignment types, move-only constructor arguments, const access, or concurrency during function-local static initialization. The destructor test is intentionally binary: any destructor call aborts the whole test process.

## Test Signals
Passing tests indicate constructor forwarding works and destructor suppression is effective in both automatic and static storage contexts.
