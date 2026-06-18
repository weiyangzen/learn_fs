## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ReplicationUtils.h

Purpose: Declares replication-policy test and analysis helpers used to evaluate locality policies and generate/filter test locality maps.

Important APIs/types/functions: Exports `convertToTestType()`, `testReplication()`, `ratePolicy()`, `findBestPolicySet()`, `findBestUniquePolicySet()`, overloads of `validateAllCombinations()`, `createTestLocalityMap()`, and `filterLocalityDataForPolicy*()` helpers.

Control flow: Implementations are elsewhere. The declared functions repeatedly apply policies to locality sets, rate uniqueness/failure characteristics, brute-force combinations, and remove locality keys not used by a policy.

State and persistence behavior: No state in the header. Helpers operate on caller-provided `LocalitySet`, `LocalityGroup`, policy references, and locality vectors.

Dependencies and integration points: Depends on `ReplicationTypes.h`, `LocalityData`, `LocalitySet`, `LocalityGroup`, and `IReplicationPolicy`. It is test/support oriented rather than core runtime selection.

Risks: These utilities can be expensive because they test many selections or combinations. Filtering locality data must preserve every attribute a policy actually uses or validation will become unsound.

Test signals: Unit tests around policy rating, best-set discovery, unique-policy selection, all-combinations validation, generated locality maps, and policy-driven locality filtering.
