# sources/storage-engines/foundationdb/fdbrpc/dsltest.actor.cpp

## Purpose
`dsltest.actor.cpp` is a broad Flow actor DSL, future/promise, allocator, arena, async map, and microbenchmark test harness. It validates actor compiler control-flow behavior, generated actor fuzz cases, promise/stream primitives, and several low-level Flow utilities.

## Important APIs, Types, and Functions
Important functions include `testFuzzActor`, actor templates `addN`, `switchTest`, `chooseTest`, `achain`, `chain2`, `cycle`, and many actor control-flow tests `actorTest1` through `actorTest10`. Utility tests include `fastAllocTest`, `arenaTest`, `asyncMapTest`, `introPromiseFuture`, `introActor`, `chainTest`, `cycleTime`, `sleeptest`, `copyTest`, and top-level `dsltest`. Local types include `TestBuffer`, `FastKey`, `TestB`, `AddReply`, and `AddRequest`.

## Control Flow
`dsltest` seeds deterministic random state, runs async map checks, a 1000-node stream cycle, introductory promise/actor examples, actor control-flow cases, generated actor fuzz tests, many promise/future/stream performance loops, arena serialization/allocation tests, choose/add examples, switch tests, fast allocator tests, and optional thread-safety tests when `FLOW_THREAD_SAFE` is enabled. `testFuzzActor` drives a generated actor five times with varied input/error timing and compares all outputs against the Python-generated oracle.

## State and Persistence Behavior
State is almost entirely transient and printed to stdout. Some routines allocate large in-memory objects, mutate global deterministic random state, increment `fastKeyCount`, and create actor futures. Disabled `#if 0` blocks contain older memory and thread tests but do not run.

## Dependencies and Integration Points
The file depends on `fdbrpc/simulator.h`, `fdbrpc/ActorFuzz.h`, Flow actor compiler, deterministic random, thread helpers, `FastRef`, arenas, serialization, promises, streams, and async maps. It integrates with generated `ActorFuzz.actor.cpp` via `actorFuzzTests()`.

## Risks and Edge Cases
The file contains many microbenchmarks and old disabled experiments rather than clean unit tests. It prints heavily and uses blocking `.get()` patterns, so it is best suited to local test binaries rather than production paths. Some actor calls are made without awaiting returned futures, relying on immediate behavior and side effects. The TODO near the top questions whether the file is still needed.

## Test Signals
Signals are stdout messages, assertions, fuzz pass counts, and absence of actor compiler/runtime failures. Actor control-flow digits `1` through `10`, `AsyncMap: OK`, and actor fuzz passed/total counts are key visible markers.
