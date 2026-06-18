# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestListStatus.java

## Purpose
`TestListStatus` asserts sorted `OzoneFileStatus` output for FSO bucket `listStatus` across full prefixes, partial prefixes, start-key cases, and bounded result sizes.

## Important APIs, Types, and Functions
- `init()` creates an FSO bucket with `OZONE_FS_ITERATE_BATCH_SIZE` set to five and builds a namespace containing directories and files under `a*` and `b*`.
- `sortedListStatusParametersSource()` defines thirteen cases for prefix, start key, requested entry count, expected result size, partial-prefix flag, and description.
- `testSortedListStatus(...)` calls `checkKeyList(...)`.
- `checkKeyList(...)` calls `fsoOzoneBucket.listStatus(prefix, false, startKey, numEntries, isPartialPrefix)`, asserts expected size, and checks strict ascending path order.

## Control Flow
Setup creates directories/files through `createDirectory` and `createFile`. Each parameterized test executes one `listStatus` call, validates count, then walks adjacent statuses and asserts each path compares less than the next.

## State and Persistence Behavior
The test persists FSO directory and file entries in OM metadata. It does not mutate global OM config except client-side iterate batch size for this client. The important observable state is sorted status order and result truncation.

## Dependencies and Integration Points
Dependencies include FSO bucket layout, `OzoneBucket.listStatus`, `OzoneFileStatus`, Ratis replication config, `TestDataUtil`, and Ozone iterate batch config.

## Risks and Test Signals
Risks include lexicographic ordering changes, partial-prefix semantics, and null start-key handling. Signals are exact result sizes and strictly increasing path comparisons.
