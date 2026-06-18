# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestContainerKeyMapperTask.java

Purpose: This suite verifies `ContainerKeyMapperTaskOBS` and `ContainerKeyMapperTaskFSO`, which maintain Recon's mapping from container IDs to key prefixes and key counts. It covers full reprocess and delta processing for key-table and file-table events.

Important APIs and types: The test uses `ReconContainerMetadataManager`, `ReconOMMetadataManager`, `ReconTestInjector`, `ContainerKeyPrefix`, `ContainerKeyMapperTaskOBS`, `ContainerKeyMapperTaskFSO`, `ContainerKeyMapperHelper`, `OMDBUpdateEvent`, `OMUpdateEventBatch`, `OmKeyInfo`, `OmKeyLocationInfo`, `OmKeyLocationInfoGroup`, `BlockID`, `Pipeline`, and `BucketLayout`. It relies on `OMMetadataManagerTestUtils` helpers to create OM metadata rows with block locations.

Control flow: `setUp` creates a fresh OM DB and Recon metadata manager, builds a Recon injector with container DB support, clears shared container-count state, and resets table truncation flags. Reprocess tests write keys with location groups containing blocks in containers 1 and 2, run the relevant mapper task, and assert stored prefixes and counts. Process tests build PUT and DELETE batches, run task `process`, and compare pre/post mappings. The duplicate FSO test writes six same-file-name rows under different parent object IDs and expects six distinct container-prefix entries.

State and persistence behavior: The suite writes OM key/file table rows and persists container-key mappings in Recon's container metadata store. It validates per-container prefix maps, per-container key counts, and total container count. FSO keys use object-ID path keys; OBS/default keys use ozone key strings. Runtime shared state in `ContainerKeyMapperHelper` is explicitly cleared between tests.

Dependencies and integration points: These tests exercise how Recon translates OM block location metadata into container-level lookup indexes used by Recon APIs. They integrate OM table encoding, bucket layout selection, block location groups, Recon container metadata persistence, and delta event handling.

Risks: Iterator order is assumed in one FSO process assertion that reads two prefixes from a map. The tests are sensitive to exact key-prefix formatting and object-ID path construction. Shared static container-count state can contaminate other tests if not reset. Some DELETE events use a value object built for a different key, so the signal is mainly container/block removal behavior rather than full key identity fidelity.

Test signals: Empty initial mappings, exact `ContainerKeyPrefix` entries with block version `0`, key count changes for containers 1, 2, and 3, total container count, deletion removing prefixes, FSO slash-prefixed user paths, and six distinct entries for duplicate file names in different directories.
