# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestUnknownContainerReport.java

## Purpose
`TestUnknownContainerReport` verifies how `ContainerReportHandler` reacts when a datanode reports a container that SCM cannot find. The test exists to guard the configurable behavior that unknown containers may either be ignored or deleted from the datanode.

## Important APIs, Types, and Functions
The test uses `ContainerReportHandler.UnknownContainerAction`, `ScmConfig.HDDS_SCM_UNKNOWN_CONTAINER_ACTION`, `ContainerReportFromDatanode`, `ContainerReportsProto`, `CommandForDatanode`, and `SCMEvents.DATANODE_COMMAND`. `setup()` creates a `MockNodeManager`, mocked `ContainerManager`, and event publisher; the mocked container manager always throws `ContainerNotFoundException.newInstanceForTesting()` from `getContainer`.

## Control Flow and State Behavior
`testUnknownContainerNotDeleted` sends a full report using a default `OzoneConfiguration`. Since no explicit unknown-container action is configured, the handler should not emit any datanode command. `testUnknownContainerDeleted` sets `HDDS_SCM_UNKNOWN_CONTAINER_ACTION` to `DELETE`, sends the same report, and verifies that one datanode command is published. `sendContainerReport` constructs the handler with `SCMContext.emptyContext()` and the supplied configuration, creates a CLOSED synthetic container only to obtain a container ID, selects an in-service healthy mock datanode, and invokes `onMessage`.

The report proto includes realistic size, usage, key-count, read/write, final hash, BCSID, and delete transaction fields. There is no persistence mutation in this test because the container manager lookup always fails and the outcome is exclusively event publication.

## Dependencies and Integration Points
This is a narrow integration point between SCM configuration, container report processing, and datanode command emission. It depends on `MockNodeManager` for a reporting datanode and on Mockito verification for the publisher side effect.

## Risks and Test Signals
The main risk is accidentally deleting unknown containers by default, or failing to delete them when the operator explicitly configures DELETE. The signal is precise: zero or one `SCMEvents.DATANODE_COMMAND` publication. The test does not inspect the exact command payload, so it validates command emission policy rather than delete-command structure.
