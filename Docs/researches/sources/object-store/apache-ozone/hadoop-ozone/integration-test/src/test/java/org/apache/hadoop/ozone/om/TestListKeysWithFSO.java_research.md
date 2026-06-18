# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestListKeysWithFSO.java

## Purpose
`TestListKeysWithFSO` validates FSO bucket `listKeys` behavior by comparing FSO output to legacy bucket output for equivalent namespaces. It covers valid and nonexistent start keys, trailing slash normalization, mixed directory/file trees, shallow listing, empty buckets, and `OzoneKey.isFile` classification.

## Important APIs, Types, and Functions
- `init()` enables filesystem path behavior, lowers max list size, configures list batch/cache sizes, creates legacy and FSO buckets in the same volume, plus empty comparison buckets.
- `buildNameSpaceTree(...)` and `buildNameSpaceTree2(...)` create two test namespaces with nested keys, flat keys, and file names that resemble directories.
- `getExpectedKeyList(...)` and `getExpectedKeyShallowList(...)` compute expected results from legacy buckets.
- `checkKeyList(...)` and `checkKeyShallowList(...)` iterate FSO results, validate replication config, collect names, and compare with expected legacy output.
- `testIsFileFalseForDir()` validates FSO listing returns a directory key with `isFile=false` followed by the real file with `isFile=true`.

## Control Flow
The main tests derive expected lists from legacy buckets for many prefix/start-key combinations, then assert the FSO bucket matches. Cases include start keys before/after prefixes, file versus directory start keys, nonexistent leaf/parent paths, empty prefix, partial prefix, mixed directories/files, shallow listing with null start key, and empty buckets.

## State and Persistence Behavior
The file creates persistent legacy and FSO bucket namespaces and temporarily mutates OM path/list-size configuration. FSO state is object-ID/path-table based internally, but the public observable state must match legacy `listKeys` names for these scenarios.

## Dependencies and Integration Points
Dependencies include FSO and legacy bucket layouts, Ozone client factory, `BucketArgs`, `StorageType`, `TestDataUtil`, Ozone list cache/batch config, replication config defaults, and Hadoop IO utilities.

## Risks and Test Signals
Risks include using legacy behavior as the oracle, path normalization differences for leading slashes, and batch-size effects. Signals are exact name-list equality with legacy output, replication config equality, and explicit `isFile` checks for directory and file entries.
