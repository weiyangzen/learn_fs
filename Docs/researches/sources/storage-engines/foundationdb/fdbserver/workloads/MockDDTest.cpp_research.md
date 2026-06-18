# sources/storage-engines/foundationdb/fdbserver/workloads/MockDDTest.cpp

## Purpose
Implementation of the common base class for mock data-distribution workloads. It builds a mock cluster/global state and provides data population strategies for derived mock DD tests.

## Important APIs, types, and functions
`MockDDTestWorkload` implements `getRandomRange`, constructor option parsing, `populateRandomStrategy`, `populateLinearStrategy`, `populateFixedStrategy`, `populateMgs`, and `setup`. It owns `sharedMgs`, mock DB size accounting, keyspace strategy parameters, byte-size limits, and simulation configuration knobs.

## Control flow
Construction enables the workload only for client 0 in simulation and reads options. `setup` builds a `BasicSimulationConfig`, creates `MockGlobalState`, initializes cluster layout and an empty mock database. Derived classes call `populateMgs`, which chooses fixed, linear, or random population, inserts synthetic keys into mock global state, computes estimated size, and traces reported total size.

## State and persistence behavior
State is fully in `MockGlobalState`; no real database keys are written. Population strategies create keys from integer keyspace offsets with value sizes determined by strategy and configured bounds.

## Dependencies and integration points
Depends on mock data-distribution classes, `BasicSimulationConfig`, deterministic random key generation, and derived mock DD workloads in the same folder.

## Risks and test signals
Risks include approximate size accounting, strategy string matching with `Value`, and a loop in total-size reporting that overwrites rather than accumulates per-server size. Signals are population traces and derived workload checks.
