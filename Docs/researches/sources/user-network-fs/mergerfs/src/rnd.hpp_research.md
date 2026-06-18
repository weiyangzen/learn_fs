# sources/user-network-fs/mergerfs/src/rnd.hpp

## Purpose
Declares the `RND` helper class used for pseudo-random branch selection.

## Important APIs, Types, and Functions
`RND::rand64()`, `rand64(max)`, and `rand64(min,max)` provide random values. The templated `shrink_to_rand_elem(std::vector<T>&)` swaps a random element to index zero and resizes the vector to one.

## Control Flow
The template is a no-op for vectors of size zero or one. For larger vectors it calls `rand64(v_.size())`, swaps, and truncates.

## State and Persistence Behavior
State lives in the implementation's global seed. The template mutates the caller's vector in place.

## Dependencies and Integration Points
Depends on `base_types.h` and `<vector>`. Used by `policy_rand` and weighted placement helpers.

## Risks and Edge Cases
The helper intentionally destroys all but one vector entry. Callers that need the full candidate set must copy first.

## Test Signals
Test empty/single/multi-element vectors, valid range guarantees, and integration with random policies.
