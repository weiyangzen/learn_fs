# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/package-info.java

## Purpose
This package descriptor labels `org.apache.hadoop.ozone.container.ec.reconstruction` as containing erasure-coding reconstruction-related classes. The comment has a spelling typo ("codding"), but the intent is clear.

## Important APIs and Types
The file exports no methods or classes. Key package types include `ECReconstructionCoordinator`, `ECReconstructionCoordinatorTask`, `ECReconstructionCommandInfo`, `ECContainerOperationClient`, and `ECReconstructionMetrics`.

## Control Flow
No runtime control flow exists in this descriptor. Runtime flow starts when SCM sends a reconstruct EC containers command, the datanode command handler creates a task, and the coordinator executes reconstruction.

## State and Persistence
No state is held or persisted. It only affects package-level documentation.

## Dependencies and Integration Points
The descriptor integrates with Java package documentation. Its package is integrated at runtime with datanode state machine construction, reconstruct-command handling, replication supervision, EC block streams, and container protocol RPCs.

## Risks and Test Signals
The documentation typo is harmless but visible in generated Javadocs. There is no direct test requirement; package behavior is covered by tests for the concrete EC reconstruction classes.
