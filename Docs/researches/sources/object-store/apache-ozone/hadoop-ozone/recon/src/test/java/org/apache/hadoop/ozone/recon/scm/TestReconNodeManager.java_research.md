# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconNodeManager.java

## Purpose
Tests `ReconNodeManager` registration, heartbeat, persisted node DB reload, operational-state synchronization from SCM, command filtering, and datanode detail updates.

## Important APIs, types, and functions
- Constructs `ReconNodeManager` with `ReconStorageConfig`, `NetworkTopologyImpl`, `ReconSCMDBDefinition.NODES`, `HDDSLayoutVersionManager`, `ReconContext`, and `EventQueue`.
- Uses `register`, `processHeartbeat`, `getNode`, `getAllNodes`, `getNodeStatus`, `getNodes`, `updateNodeOperationalStateFromScm`, and `addDatanodeCommand`.
- Tests `ReconNewNodeHandler`, `RegisteredCommand`, `ReregisterCommand`, and `SetNodeOperationalStateCommand`.

## Control flow
Setup creates a temp Recon SCM DB and context. One test registers a datanode with invalid network topology and expects registration rejection plus ReconContext health/error updates. The main DB test registers a node, runs new-node handling, injects both an illegal operational-state command and a valid reregister command, verifies heartbeat returns only the valid command, updates persisted operational state via heartbeat, closes and recreates the manager, and checks the node was reloaded. Another test applies an SCM node operational-state update after proving unregistered nodes throw `NodeNotFoundException`. The final test confirms heartbeat updates changed hostname and returns reregister.

## State and persistence behavior
Datanode records are persisted in the Recon SCM `NODES` table and reloaded after manager recreation. Node status mirrors persisted operational state and expiry. ReconContext records invalid-topology errors and unhealthy state when registration is not permitted.

## Dependencies and integration points
This file covers the Recon variant of SCM node management, network topology validation, heartbeat command filtering, node DB persistence, and synchronization of SCM-sourced operational state into Recon's local node table.

## Risks and edge cases
Recon must not send SCM-only commands such as `SetNodeOperationalStateCommand` back to datanodes. Invalid topology must not partially register nodes. Persisted operational state and node status can drift if heartbeat update logic or reload logic changes.

## Test signals
Signals include registration error code, ReconContext error/health state, node counts, node lookup null/non-null results, heartbeat returned command types, persisted operational state/expiry equality, node reload from DB, thrown `NodeNotFoundException`, and hostname update.
