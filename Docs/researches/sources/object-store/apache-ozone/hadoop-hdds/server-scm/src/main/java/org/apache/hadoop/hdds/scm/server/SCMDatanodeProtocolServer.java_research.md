# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMDatanodeProtocolServer.java

Purpose: `SCMDatanodeProtocolServer` hosts the protobuf RPC endpoint used by datanodes for version negotiation, registration, and heartbeats.

Important APIs and types: It implements `StorageContainerDatanodeProtocol` and `Auditor`. The constructor creates an RPC server for `StorageContainerDatanodeProtocolPB`, configures metrics and ACLs, and creates a `SCMDatanodeHeartbeatDispatcher`. Main RPCs are `getVersion`, `register`, and `sendHeartbeat`. `getCommandResponse` converts in-memory `SCMCommand<?>` instances to protobuf command messages.

Control flow: `getVersion` delegates to `NodeManager`. `register` converts extended datanode details, delegates registration to `NodeManager`, and on success fires a registration full-container report, node-registration container report, and pipeline report before returning a protobuf registered response. `sendHeartbeat` dispatches reports, converts returned commands, optionally includes the current Ratis leader term, and audits the response. Command conversion switches over supported command types including reregister, delete blocks, close/delete/replicate/reconcile container, reconstruct EC, create/close pipeline, operational state, finalize layout, and refresh volume usage.

State and persistence behavior: The server owns RPC and metrics state only. Registration, heartbeat state, command queues, and layout version state are managed by `NodeManager` and downstream event handlers.

Dependencies and integration points: It integrates datanodes with SCM node manager, event queue, heartbeat dispatcher, HA leader term publication, protocol metrics, audit logging, service ACLs, and Recon-friendly override points for bind address, policy provider, protocol class, and metrics creation.

Risks: Adding a new `SCMCommand` type requires updating `getCommandResponse` or heartbeats will fail with `IllegalArgumentException`. Registration fires reports only after successful registration. `stop()` unregisters metrics after stopping RPC and cleans up the shared node manager.

Test signals: Tests should verify RPC binding, version delegation, registration event firing, heartbeat command protobuf conversion for every command type, leader term inclusion only on leaders, audit logs, unsupported command failure, and subclass override points.
