## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/UpgradeTestHelper.java

Purpose: Shared utility class for datanode upgrade tests, reducing boilerplate for starting/restarting pre-finalized datanodes, configuring volumes, and dispatching container commands.

Important APIs/types/functions: `startPreFinalizedDatanode`, `restartDatanode`, `callVersionEndpointTask`, `addHddsVolume`, `addDbVolume`, `dispatchRequest`, `readChunk`, `putBlock`, `addContainer`, `deleteContainer`, `closeContainer`, and `finalizeBlock`.

Control flow: Startup helper writes layout storage with requested metadata layout version, closes any prior DSM, starts a new `DatanodeStateMachine`, asserts MLV, and calls the version endpoint task to obtain SCM/cluster IDs. Restart helper preserves datanode details, optionally sets DB parent dirs, validates MLV exact or lower-bound, and calls version endpoint. Command helpers construct requests via `ContainerTestHelper`, dispatch them, and assert expected results.

State and persistence behavior: Mutates `OzoneConfiguration` volume path lists, creates temporary HDDS/DB volume directories, initializes datanode layout storage, and sends real dispatcher commands that create/write/close/delete containers.

Dependencies and integration points: Central integration layer for SCM RPC, endpoint state machine, Ozone container, container dispatcher, pipelines, and upgrade feature tests.

Risks and test signals: Helper correctness is critical because multiple upgrade suites inherit its assumptions. Random container IDs can collide theoretically. Assertions inside helpers make failures concise but can hide intermediate protocol details.
