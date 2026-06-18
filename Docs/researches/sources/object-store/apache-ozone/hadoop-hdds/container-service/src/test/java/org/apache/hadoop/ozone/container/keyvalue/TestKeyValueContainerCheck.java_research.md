# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerCheck.java

Purpose: validates `KeyValueContainerCheck` scanner behavior for metadata failures, data corruption aggregation, checksum-tree diffs, normal containers, corrupted chunks, and containers marked for deletion.

Important APIs/types/functions: extends `TestKeyValueContainerIntegrityChecks`; uses `KeyValueContainerCheck.fastCheck/fullCheck`, `DataScanResult`, `ContainerScannerConfiguration`, `DataTransferThrottler`, `ContainerChecksumTreeManager.updateTree/diff`, `ContainerDiffReport`, and `TestContainerCorruptions`. Parameter sources exclude unsupported file-per-chunk corruption injection for fault-injection cases.

Control flow: metadata-error tests create a valid container, verify a clean full scan, inject one metadata corruption and optionally a later data corruption, then assert scan exits after the metadata error only. Data-error aggregation creates six blocks, captures a healthy Merkle tree, corrupts one block, deletes one block, truncates another, runs full scan, checks ordered failure types, writes the new corrupted tree, and verifies diff reports corrupt chunks, missing chunks, and missing blocks. Sanity tests cover clean open/closed scans and a manually truncated chunk failure. Deleted-container tests show missing internals are errors before `markContainerForDelete()` and become deleted/non-error scan results after deletion marking.

State and persistence behavior: tests create real block files, DB metadata, container YAML, and checksum tree updates. Corruption mutates files/directories on disk; scans read metadata first and then data files. Marking a container for delete changes scan semantics so missing directories are treated as expected deletion state.

Dependencies and integration points: integrates scanner config, throttling/cancel APIs, checksum tree manager, block iterator, layout file resolution, and reusable corruption enum. It protects both scan error reporting and reconciliation diff inputs.

Risks and test signals: strong signals for scanner stop/continue policy: metadata errors short-circuit, data errors accumulate. The expected duplicate corrupt-chunk and all-chunks-missing behavior encodes current scanner interpretation and may need adjustment if scanner granularity changes.
