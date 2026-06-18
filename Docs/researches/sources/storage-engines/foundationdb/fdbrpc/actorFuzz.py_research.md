# sources/storage-engines/foundationdb/fdbrpc/actorFuzz.py

## Purpose
`actorFuzz.py` generates `ActorFuzz.actor.cpp`, a randomized suite of Flow actor control-flow tests. It creates actor functions with loops, waits, throws, returns, breaks, continues, try/catch blocks, and range-for loops, then computes expected output by interpreting the generated structure in Python.

## Important APIs, Types, and Functions
Generation state lives in `Context`; interpretation state lives in `ExecContext`. AST-like node classes include `hashF`, `compoundF`, `loopF`, `rangeForF`, `ifF`, `tryF`, `breakF`, `continueF`, `waitF`, `throwF`, `throwF2`, `throwF3`, and `returnF`. `fuzzCode` chooses node types, and `randomActor` builds one complete actor and expected-output list.

## Control Flow
The script opens `ActorFuzz.actor.cpp`, writes a header, includes `ActorFuzz.h`, skips Windows, generates 30 actors, and writes `actorFuzzTests()` that calls `testFuzzActor` for each generated actor with the expected outputs. `randomActor` retries on interpreted infinite loops, appends a fallback return, evaluates the AST against an infinite input sequence, and records final return or error code output.

## State and Persistence Behavior
The script persists one generated C++ file in the current working directory. Randomness is not seeded explicitly, so generated content changes across invocations. Class attributes such as `Context.tok`, `Context.indent`, and `ExecContext.iterationsLeft` are overridden per instance where needed.

## Dependencies and Integration Points
It depends only on Python `random` and `copy`. The generated C++ depends on Flow actor syntax and `fdbrpc/ActorFuzz.h`, and is consumed by `dsltest.actor.cpp` through `actorFuzzTests()`.

## Risks and Edge Cases
Unseeded generation makes diffs non-reproducible unless callers control Python randomness externally. The output path is relative, so running from the wrong directory writes the generated file elsewhere. The interpreter is a model of actor behavior, not the actor compiler itself; mismatches can reflect either compiler bugs or generator-model bugs. Python 3 style is mostly used, but the script has no command-line contract or deterministic manifest.

## Test Signals
The generated `actorFuzzTests()` returns passed/total counts. `dsltest()` prints the count and exercises each actor five times with different input/error timing through `testFuzzActor`.
