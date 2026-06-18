# sources/user-network-fs/mergerfs/src/rnd.cpp

## Purpose
Implements a lightweight process-local pseudo-random generator used by random placement policies.

## Important APIs, Types, and Functions
The constructor-marked `_constructor()` seeds `G_SEED` from `gettimeofday()`. `_rapidhash_rand()` advances the seed and calls `rapid_mix()`. `RND::rand64()` returns raw random values, modulo `[0,max)`, or `[min,max)`.

## Control Flow
The seed is initialized before normal program execution. Each random call mutates `G_SEED`, and bounded calls assert valid ranges before using modulo reduction.

## State and Persistence Behavior
`G_SEED` is a process-global mutable value and is not synchronized. No persistent storage is used.

## Dependencies and Integration Points
Depends on `rapidhash/rapidhash.h`, `base_types`, and random policy code such as `rand`, `pfrd`, and `msppfrd`.

## Risks and Edge Cases
The generator is not cryptographic, is not thread-safe, and bounded values have modulo bias. Assertions disappear in release builds, so callers must avoid zero or invalid bounds.

## Test Signals
Test bounded ranges, seed mutation, repeat-run variability, invalid-bound assertions in debug builds, and concurrent policy stress if used from multiple threads.
