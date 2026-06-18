## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestContainerImporter.java

Purpose: Tests `ContainerImporter` duplicate protection, in-progress tracking, checksum consistency validation, imported-container scanning, failure-triggered volume handling, and reset of last scan time.

Important APIs/types/functions: `ContainerImporter.importContainer`, `getImportContainerProgress`, `getKeyValueContainerData`, `getPacker`, `ContainerController.importContainer`, `ContainerSet.scanContainer`, `StorageVolumeUtil.onFailure`, `TarContainerPacker`, and `ContainerDataYaml`.

Control flow: Setup builds a real `MutableVolumeSet`, `ContainerSet`, and spy/mocked controller. Tests reject an existing container, reject a second import while the first is blocked on a semaphore, force inconsistent container checksums, import a tar descriptor and verify scanner invocation, mock import failure to verify volume failure callback, and assert imported data scan timestamp becomes empty.

State and persistence behavior: Creates real temporary tar files containing `container.yaml`. Tracks import-in-progress IDs in the importer and mutates `KeyValueContainerData` scan timestamp.

Dependencies and integration points: Integrates tar packing, volume choosing, controller import, volume failure utility, and container-set on-demand scanning.

Risks and test signals: Strong signal for duplicate/import-progress races and cleanup. Some paths use spies and static mocking, so internal method names are coupled to tests.
