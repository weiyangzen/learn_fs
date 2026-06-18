# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/InvalidNodeStateException.java

Purpose: `InvalidNodeStateException` is a checked exception thrown when an admin operation such as decommission or maintenance is requested for a datanode in an incompatible operational state.

Important APIs and types: It extends `IOException` with message-only and message-plus-cause constructors.

Control flow: The exception is thrown by `NodeDecommissionManager.startDecommission` and `startMaintenance` when a node is not `IN_SERVICE`, already in the relevant workflow, or otherwise not eligible. Higher-level bulk methods convert it to `DatanodeAdminError`.

State and persistence behavior: The class stores only standard exception message/cause. It does not mutate state; the caller should throw it before changing node operational state.

Dependencies and integration points: It links node status validation to admin APIs and CLI-visible error paths. It is part of the decommission-manager API contract.

Risks: The class Javadoc currently says "host strings", which appears copied from `InvalidHostStringException` and can mislead maintainers. Message wording is likely asserted by admin-path tests or visible to users.

Test signals: Tests should verify that invalid state transitions throw this exception without calling `setNodeOperationalState` and that bulk admin APIs surface its message in error results.
