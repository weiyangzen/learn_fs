# sources/storage-engines/foundationdb/flow/include/flow/unactorcompiler.h

## Purpose
This small cleanup header undefines actor compiler macros after actor-generated or actor-aware code has been processed. It prevents Flow actor keywords/macros from leaking into ordinary C++ code.

## Important APIs, Types, and Functions
There are no functions or types. The header conditionally undefines `ACTOR`, `SWIFT_ACTOR`, `state`, `UNCANCELLABLE`, `choose`, and `when` when `NO_INTELLISENSE` is not defined, and always undefines `THIS` and `THIS_ADDR` inside the `!POST_ACTOR_COMPILER` branch. A comment notes that `loop` remains defined.

## Control Flow
All behavior is preprocessor control flow. If `POST_ACTOR_COMPILER` is not defined, the cleanup runs. If `NO_INTELLISENSE` is defined, it preserves some actor macros for IDE parsing while still undefining `THIS` and `THIS_ADDR`.

## State and Persistence Behavior
No runtime state exists. The header mutates preprocessor state for the rest of the translation unit, which is its entire purpose.

## Dependencies and Integration Points
It integrates with FoundationDB's actor compiler and headers that temporarily define actor-language macros. It is usually paired with actor compiler include boundaries to restore normal C++ macro space.

## Risks
Include ordering is the only real risk. Including it too early can remove actor macros before they are needed; including it too late can let macros corrupt unrelated code. Leaving `loop` defined is intentional but still a possible macro collision. IntelliSense-specific branching can differ from real compiler behavior.

## Test Signals
Actor-compiled and non-actor translation units should compile with this header at expected boundaries. Preprocessor tests can verify macros are present before and absent after inclusion, with separate coverage for `NO_INTELLISENSE` and `POST_ACTOR_COMPILER`.
