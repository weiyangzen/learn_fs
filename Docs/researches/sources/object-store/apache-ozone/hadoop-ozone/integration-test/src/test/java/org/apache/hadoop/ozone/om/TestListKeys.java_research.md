# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestListKeys.java

## Purpose
`TestListKeys` validates `OzoneBucket.listKeys(keyPrefix, startKey, shallow)` behavior for legacy and object-store bucket layouts. It stresses trailing-slash and non-trailing-slash prefixes, start-key ordering, shallow directory projection, replication metadata, and pagination-related batch settings.

## Important APIs, Types, and Functions
- `init()` enables filesystem path behavior, temporarily lowers OM max list size, configures client list/cache batch sizes, creates LEGACY and OBJECT_STORE buckets, and builds identical namespace trees.
- `buildNameSpaceTree(...)` creates a nested key tree and an explicit directory `a1/b4/`.
- Parameter sources define expected shallow-list outputs for trailing-slash and non-trailing-slash cases, with OBS-specific expectations where prefix directory entries differ.
- `checkKeyShallowList(...)` calls `bucket.listKeys(prefix, startKey, true)`, validates replication config on each `OzoneKey`, collects names, and asserts exact order/content.

## Control Flow
Setup creates both bucket layouts and writes the same tree. Parameterized tests feed prefix/start-key/expected-list tuples. The checker iterates the returned keys and compares to expected linked lists, printing diagnostics around each case.

## State and Persistence Behavior
The namespace consists of persisted keys and directory markers in two bucket layouts. The test temporarily mutates OM config (`fileSystemPathEnabled`, `maxListSize`) and restores it after all tests. Client-side list cache and server-side batch sizes are reduced to make list iteration cross batch boundaries.

## Dependencies and Integration Points
Dependencies include `NonHATests`, Ozone client factory, bucket layouts, `TestDataUtil.createStringKey`, Hadoop IO utilities, OM config, Ozone list cache/batch config, and replication config defaults.

## Risks and Test Signals
Risks include subtle layout-specific directory marker behavior and start-key inclusivity rules. Signals are exact ordered key-name lists for each case and replication config equality for every returned key.
