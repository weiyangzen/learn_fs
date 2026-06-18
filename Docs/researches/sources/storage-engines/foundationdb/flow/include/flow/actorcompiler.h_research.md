# sources/storage-engines/foundationdb/flow/include/flow/actorcompiler.h

## Purpose
Provides actor-compiler and IDE macros for Flow actor syntax and compile-time guards that catch unre-written `wait` usage after actor compilation.

## Important APIs, Types, And Functions
Under `POST_ACTOR_COMPILER`, `wait` and `waitNext` overloads are deleted. For IntelliSense, it defines `ACTOR`, `SWIFT_ACTOR`, `state`, `UNCANCELLABLE`, `choose`, `when`, and placeholder wait functions. It also defines `loop`, `THIS`, `THIS_ADDR`, and Valgrind no-op macros when needed.

## Control Flow
Preprocessor state determines whether source is actor-authoring-friendly or post-compiler-safe. Actor files include this last so the actor compiler can rewrite constructs before C++ compilation.

## State And Persistence Behavior
No runtime state or persistence.

## Dependencies And Integration Points
Tightly coupled to `.actor.*` files, generated `.actor.g.h`, `unactorcompiler.h`, Flow coroutine support, and IDE parsing.

## Risks And Edge Cases
Common macro names can collide outside actor contexts. Weakening deleted post-compiler waits could let raw actor syntax compile incorrectly. Conditional compilation inside actors is constrained.

## Test Signals
Actor compilation success, deliberate raw `wait` failure after compilation, IDE parseability, and Flow actor line-number/cancellation tests.
