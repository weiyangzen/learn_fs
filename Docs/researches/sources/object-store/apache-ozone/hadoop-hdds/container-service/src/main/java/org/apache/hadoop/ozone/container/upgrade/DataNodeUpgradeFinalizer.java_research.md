# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/DataNodeUpgradeFinalizer.java

Purpose: datanode-specific layout upgrade finalizer.

Important APIs and functions: the constructor accepts an `HDDSLayoutVersionManager`. `preFinalizeUpgrade` verifies finalization is safe, resets state to `FINALIZATION_REQUIRED` and throws `PREFINALIZE_VALIDATION_FAILED` if not, otherwise moves to `FINALIZATION_IN_PROGRESS`. `canFinalizeDataNode` scans all containers and refuses finalization while any container is `OPEN` or `CLOSING`. `finalizeLayoutFeature` accepts only `HDDSLayoutFeature`, then delegates to `BasicUpgradeFinalizer` with the feature's datanode action and layout storage.

Control flow and state: finalization is gated on container closure, preventing layout transitions while active writes are still possible. Version manager state is the durable finalization cursor managed by the base finalizer.

Dependencies and integration: called by datanode upgrade handling in the state machine. It integrates container controller iteration, layout storage, HDDS feature actions, and Ozone upgrade exceptions.

Risks and test signals: failure to block open containers could corrupt layout migrations; overblocking could stall upgrades. Tests should cover open, closing, closed, quasi-closed, and unhealthy container states; non-HDDS feature rejection; state reset on failed precheck; and action invocation ordering.
