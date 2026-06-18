# sources/storage-engines/foundationdb/flow/LinkTest.cpp

## Purpose
Provides a dummy executable `main()` so module link tests fail on unresolved symbols instead of allowing static/shared libraries to hide them.

## Important APIs, Types, And Functions
`int main()` returns `0`.

## Control Flow
No logic beyond process entry and success exit.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Used by build targets that intentionally link module objects into an executable to validate symbol closure.

## Risks And Edge Cases
The file only proves linkability for objects included in the executable target; missing objects can still evade the check if the build target is incomplete.

## Test Signals
Successful build/link of the target is the signal.
