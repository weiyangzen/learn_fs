# sources/distributed-fs/tahoe-lafs/integration/vectors/model.py

## Purpose
Defines small immutable data models used to describe vector inputs and ZFEC parameters.

## Important APIs, Types, and Functions
`MAX_SHARES` is a symbolic sentinel. `Sample` stores a seed byte string and target length. `Param` stores realized `required` and `total` share counts. `SeedParam` stores `required` and either a concrete total or `MAX_SHARES`; `realize(max_total)` returns a concrete `Param`.

## Control Flow
The only logic is `SeedParam.realize`: substitute `max_total` when `total == MAX_SHARES`, otherwise preserve the configured total.

## State and Persistence
No persistence. Instances are frozen `attrs` values suitable as deterministic vector-case components.

## Dependencies and Integration Points
Depends on `attrs.frozen` and Python union types. Used by parameter definitions and vector serialization/loading.

## Risks
`MAX_SHARES` is a string sentinel, so accidental user-supplied string equality could trigger substitution. There is no validation that `required <= total` or that totals are within CHK/SSK bounds; callers are responsible for using valid parameter sets.

## Test Signals
Signals come indirectly from vector generation and capability tests; incorrect realization changes produced capabilities or causes upload failures.
