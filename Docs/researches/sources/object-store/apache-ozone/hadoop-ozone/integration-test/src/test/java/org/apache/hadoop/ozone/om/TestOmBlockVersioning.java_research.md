# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmBlockVersioning.java

Purpose: This abstract non-HA integration test preserves OM-side block versioning behavior for key open, block allocation, commit, overwrite, and read-latest semantics. It documents the current behavior that bucket versioning is not generally supported, while explicit open/commit updates can still produce sequential location versions.

Important APIs and types: The file uses `OzoneClient`, `OzoneManager`, `OzoneManagerProtocol`, `OzoneBucket`, `TestDataUtil`, `OmKeyArgs`, `OpenKeySession`, `OmKeyInfo`, `OmKeyLocationInfo`, `OmKeyLocationInfoGroup`, `ExcludeList`, `StandaloneReplicationConfig`, and protobuf replication factor `ONE`.

Control flow: `testAllocateCommit` creates a volume/bucket/key, calls `bucket.setVersioning(true)` to preserve historical behavior, then performs three `openKey`/`commitKey` cycles. The first two commits use the latest open-key block list directly. The third allocates an additional block through `allocateBlock`, appends it to the latest location list, commits, and checks that versions are sequential and the latest version has two blocks. `testReadLatestVersion` creates and overwrites a key through normal client IO while versioning is disabled and checks reads and OM lookup always expose version 0 with one block.

State and persistence behavior: Persistent state is OM key metadata: location version groups, block lists, and latest version selected by lookup/read. The first test expects multiple version groups after explicit commits, while the second expects overwrites without bucket versioning to reset/remain at version 0 rather than accumulating visible versions.

Dependencies and integration points: It integrates OM protocol open/commit/allocate calls, client key creation/read helpers, replication config, SCM block allocation through OM, and `OzoneManager.lookupKey`.

Risks: The tests encode legacy compatibility around unsupported bucket versioning. If full versioning support changes overwrite semantics, these assertions will need intentional updates. They do not validate block contents, only metadata version and block-count behavior.

Test signals: Signals include sequential version numbers from `checkVersions`, latest versions 0, 1, and 2 after explicit commit cycles, latest location-list sizes of one/one/two, normal overwrite reads returning the newest data string, and latest version staying 0 with one block when versioning is disabled.
