# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/OzoneTestUtils.java

Purpose: shared Ozone integration-test utilities for closing containers, operating on containers that back a key, asserting OM exceptions, flushing deleted block logs, and waiting for block deletion.

Important APIs/types/functions: `triggerCloseContainerEvent`, `closeContainers`, `closeAllContainers`, `performOperationOnKeyContainers`, `expectOmException`, `closeContainer`, `flushAndWaitForDeletedBlockLog`, `waitBlockDeleted`. It integrates with `StorageContainerManager`, `SCMEvents`, `EventPublisher`, `OmKeyLocationInfoGroup`, `BlockID`, `ContainerInfo`, `Pipeline`, and OM/SCM metadata APIs.

Control flow: key-container operations iterate key location groups and each `OmKeyLocationInfo`, extract `BlockID`, and pass it to a checked consumer. Triggering close fires `SCMEvents.CLOSE_CONTAINER`; direct close transitions OPEN containers through FINALIZE and CLOSING containers through CLOSE, then asserts the container is not open. `closeAllContainers` fires close events for every SCM container. `expectOmException` wraps a callable and compares result code. `closeContainer` closes the container's pipeline and waits until the `ContainerInfo` state becomes CLOSED. Deleted-block helpers repeatedly flush the SCM HA transaction buffer and poll valid transaction count until nonzero or zero.

State and persistence: observes and mutates SCM container lifecycle state, event queue, pipeline state, SCM HA transaction buffer, and deleted block log. No independent storage.

Dependencies and integration points: SCM event framework, container manager state machine, pipeline manager, OM key-location metadata, `GenericTestUtils.waitFor`, `LambdaTestUtils.VoidCallable`, and Ratis checked consumers.

Risks: direct state transitions can bypass parts of normal datanode reporting. `closeContainer` waits on the passed `ContainerInfo` object, which must reflect updates. Deleted-block helpers swallow IOExceptions inside polling lambdas, potentially hiding transient failures until timeout. `closeAllContainers` is asynchronous because it only fires events.

Test signals: downstream tests use these helpers to assert specific OM exception codes, force/observe container closure, and wait for deleted block log state transitions.
