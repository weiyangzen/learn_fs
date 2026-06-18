# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerProtocolServer.java

Purpose: Server-side datanode implementation of `DiskBalancerProtocol` for reading disk balancer status and starting, stopping, or updating service configuration.

Important APIs and types: Implements `getDiskBalancerInfo`, `startDiskBalancer`, `stopDiskBalancer`, `updateDiskBalancerConfiguration`, and `close`. Uses a `PrivilegedOperation` functional interface for admin authorization.

Control flow: Read-only info requires no admin check. Start/update/stop call `adminChecker`. Start checks datanode operational state: IN_SERVICE becomes RUNNING, otherwise PAUSED. Optional config proto is merged into current persisted config using `DiskBalancerConfiguration.updateFromProtobuf`, then `refreshService` applies and persists it through the service.

State and persistence: Does not store state locally. It mutates `DiskBalancerInfo`, and `DiskBalancerService.refresh` persists the resulting state.

Dependencies and integration points: Bridges RPC clients to `DatanodeStateMachine`, `OzoneContainer`, and `DiskBalancerService`. Info responses include datanode details, config, counters, bytes, status, ideal usage, and volume reports.

Risks: If service is disabled, operations throw `IOException`. Start on non-IN_SERVICE nodes persists PAUSED, not STOPPED, which affects later resume behavior. Tests should cover admin enforcement, disabled service errors, node-state-dependent start behavior, partial proto updates, and response field population.
