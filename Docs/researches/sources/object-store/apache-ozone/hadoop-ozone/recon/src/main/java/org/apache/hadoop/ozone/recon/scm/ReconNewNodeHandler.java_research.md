## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconNewNodeHandler.java

Purpose: `ReconNewNodeHandler` persists newly registered DataNodes into Recon's SCM node DB asynchronously from the event path.

Important APIs and types: implements `EventHandler<DatanodeDetails>`, stores a `ReconNodeManager`, and implements `onMessage(DatanodeDetails, EventPublisher)`.

Control flow: when `SCMEvents.NEW_NODE` fires, the handler calls `nodeManager.addNodeToDB`. Errors are logged and not rethrown, so event processing continues.

State and persistence: writes `DatanodeDetails` keyed by `DatanodeID` to the `NODES` column family in `ReconSCMDBDefinition`.

Dependencies and integration points: registered by `ReconStorageContainerManagerFacade`. Works with `ReconNodeManager.register`, which handles in-memory registration and may update existing DB entries; this handler covers the new-node DB insert after registration.

Risks and edge cases: failures leave a node in memory but absent from DB, so it may be lost across restart until it re-registers. The class stores its manager in a mutable non-final field, but it is initialized once in practice.

Test signals: no direct test was found. Useful tests would assert DB insertion on event and non-fatal logging on `IOException`.
