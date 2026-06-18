# sources/security-integrity/selinux/python/sepolgen/tests/test_access.py

## Purpose
This unit test file validates sepolgen access-vector data structures and conversions between reference-policy rules and normalized access vectors. It is focused on object construction, list/string serialization, comparisons, extended permissions, and grouped `AccessVectorSet` behavior.

## Important Tests And Exercised APIs
`TestAccessVector` covers `AccessVector` default state, `from_list`, `to_list`, `to_string`/`__str__`, ordering/equality, plain permission merge, and extended permission merge by operation. It uses `refpolicy.IdSet` and `refpolicy.XpermSet`.

`TestUtilFunctions` covers `is_idparam()` and `avrule_to_access_vectors()`, confirming cartesian expansion across source types, target types, object classes, and permissions from a `refpolicy.AVRule`.

`TestAccessVectorSet` covers creation, iteration, length, list round-trips, adding first and subsequent vectors, merging permissions under the same source/target/class/type key, storing audit messages, and the convenience `add()` wrapper.

## Control Flow
The tests construct policy objects directly, mutate their public attributes, then assert normalized data. `setUp()` builds an `AVRule`, converts it to eight access vectors, and inserts them into an `AccessVectorSet` used by multiple tests.

## State And Persistence
All state is in-memory except the shared `self.s` fixture per test case. `AccessVectorSet` internal state is validated through iteration, length, and `to_list()`, plus direct access to `src['foo']['bar']['file', av.type].audit_msgs`.

## Dependencies And Integration Points
The file imports `sepolgen.refpolicy`, `sepolgen.refparser`, `sepolgen.policygen`, and `sepolgen.access`; only `refpolicy` and `access` are materially used in the tests. It checks the contract that policy generators and audit parsers depend on: normalized access vectors must merge and compare predictably.

## Risks And Edge Cases
Two methods named `text_merge_xperm1` and `text_merge_xperm2` appear intended as tests but do not start with `test_`, so unittest will not execute them. Their assertions also expect merged plain permissions that are not present in the constructed inputs, suggesting they may be stale. Ordering assertions against set-like structures are partly normalized with sorting, but some direct `list(...)` assertions still rely on deterministic behavior from local types.

## Test Signals
This file is a strong signal for access-vector serialization, xperm merge semantics, and `AccessVectorSet` deduplication. It does not exercise parsing from actual policy text, despite importing parser modules.
