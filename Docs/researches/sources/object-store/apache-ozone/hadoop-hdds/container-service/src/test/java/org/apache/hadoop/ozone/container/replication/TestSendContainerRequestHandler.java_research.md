## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestSendContainerRequestHandler.java

Purpose: Tests server-side handling of pushed container data, especially duplicate rejection and committed-space reservation/release across normal completion and failures.

Important APIs/types/functions: `SendContainerRequestHandler.onNext`, `onCompleted`, `ContainerImporter.isAllowedContainerImport`, `chooseNextVolume`, `importContainer`, `getRequiredReplicationSpace`, `getDefaultReplicationSpace`, `SendContainerRequest`, and `SendContainerResponse`.

Control flow: Setup creates real volume/importer infrastructure and spies the importer. Existing-container test adds a container then verifies `onError` receives `StorageContainerException(CONTAINER_EXISTS)`. Parameterized reservation tests cover null, zero, normal 2GB, and overallocated 20GB size fields. They assert committed bytes rise on first request and return to initial values on completion, on `onNext` import denial, and when `importContainer` throws during completion. Overallocated test compares explicit size reservation against default reservation.

State and persistence behavior: Uses real `MutableVolumeSet` committed-byte accounting and temporary directories. Handler tracks selected target volume and temporary received data until completion.

Dependencies and integration points: Bridges gRPC upload protocol, importer capacity planning, volume reservation, and response observer error propagation.

Risks and test signals: Strong leak-prevention coverage for reservation cleanup. It does not inspect the temporary file contents beyond request creation.
