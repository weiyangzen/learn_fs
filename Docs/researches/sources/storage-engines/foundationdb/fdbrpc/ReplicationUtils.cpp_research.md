# sources/storage-engines/foundationdb/fdbrpc/ReplicationUtils.cpp

## Purpose
`ReplicationUtils.cpp` implements helper algorithms and randomized test scaffolding for FoundationDB replication policies. It evaluates policy selection fairness, finds reduced locality subsets that still satisfy a policy, validates combinations against policy constraints, builds synthetic locality maps, generates static and random policies, and exposes a unit test for the replication policy machinery.

## Important APIs, Types, and Functions
Key production-facing helpers include `ratePolicy`, `findBestPolicySet`, `findBestUniquePolicySet`, `validateAllCombinations`, `filterLocalityDataForPolicyDcAndProcess`, and the overloaded `filterLocalityDataForPolicy` variants. Test helpers include `createTestLocalityMap`, `getStaticPolicies`, `randomAcrossPolicy`, `testPolicy`, and `testReplication`. The code operates on `LocalitySet`, `LocalityMap<repTestType>`, `LocalityGroup`, `LocalityData`, `LocalityEntry`, and `IReplicationPolicy` implementations such as `PolicyOne`, `PolicyAcross`, and `PolicyAnd`.

## Control Flow
`findBestPolicySet` specializes the common `One` and `Across(zoneid, One)` shapes, then falls back to `findBestPolicySetExpensive`, which repeatedly samples policy solutions, adds random extras, restricts the locality set, rates the restricted set with repeated selections, and keeps the lowest mode concentration. `findBestUniquePolicySet` follows the same sample/rate structure while excluding entries that share the configured uniqueness key. `validateAllCombinations` clones an existing locality group, appends candidate items, enumerates bitmask combinations, and checks whether policy selection returns empty/non-empty results according to the requested validity expectation. `testReplication` reads `REPLICATION_*` environment controls, builds a synthetic locality map, chooses static or random policies, samples included servers, and either runs `findBestPolicySet` or validates `testPolicy`.

## State and Persistence Behavior
The file is mostly stateless aside from deterministic random use, `g_replicationdebug`, environment variables, policy caches from `getStaticPolicies`, and cached locality-set internals reset during tests. It does not persist cluster data. It mutates passed `LocalitySet` entries during randomized selection and strips fields from `LocalityData` in the filter helpers.

## Dependencies and Integration Points
It depends on `fdbrpc/ReplicationUtils.h`, `ReplicationPolicy.h`, `Replication.h`, `flow/Hash3.h`, `flow/Platform.h`, and `flow/UnitTest.h`. It integrates with the unit-test runner through `TEST_CASE("/fdbrpc/Replication/test")`, with simulation via `g_network->isSimulated()` assertions comparing simple and expensive algorithms, and with data-distribution style callers that need locality data reduced to policy-relevant keys.

## Risks and Edge Cases
`findBestPolicySetSimple` resizes `randomizedEntries` and then also pushes vectors, leaving leading empty vectors; the loop still works only because it cycles until enough entries are collected, but the extra empties are inefficient and fragile. The expensive search is randomized and can be costly for large policy/test counts. `filterLocalityDataForPolicyDcAndProcess` inserts dc/process keys but then calls `filterLocalityDataForPolicy(policy->attributeKeys(), ld)` instead of the augmented key set, so the function name and local inserts appear inconsistent. `validateAllCombinations` enumerates combinations exponentially and assumes `selectReplicas` succeeds.

## Test Signals
The direct signal is `/fdbrpc/Replication/test`, which forces validation and stop-on-error, then expects `testReplication()` to return zero errors. Benchmarks in this subset also call `createTestLocalityMap` and `PolicyAcross::selectReplicas`, providing performance signals for selected policy shapes.
