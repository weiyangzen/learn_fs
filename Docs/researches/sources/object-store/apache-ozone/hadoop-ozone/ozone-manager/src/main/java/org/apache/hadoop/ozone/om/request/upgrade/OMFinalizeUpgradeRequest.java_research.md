
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/OMFinalizeUpgradeRequest.java

Purpose: Handles upgrade finalization requests, invokes OM finalization logic, and persists the resulting metadata layout version.

Important APIs and types: Extends `OMClientRequest`; uses `FinalizeUpgradeRequest/Response`, `UpgradeFinalizationStatus`, `StatusAndMessages`, `LAYOUT_VERSION_KEY`, `metaTable`, and `OMFinalizeUpgradeResponse`.

Control flow: Validation checks admin authorization, reads the upgrade client ID, calls `ozoneManager.finalizeUpgrade`, converts finalization status into protobuf, reads the current metadata layout version, writes it to the metadata table cache, builds the finalize response, audits, and returns an error response with layout version `-1` on IO failure.

State and persistence behavior: Updates `LAYOUT_VERSION_KEY` in OM meta table cache at the transaction index. Finalization may also mutate version-manager state through `ozoneManager.finalizeUpgrade`.

Dependencies and integration points: Integrates layout-version manager, upgrade finalization subsystem, admin ACLs, OM metadata persistence, and audit.

Risks: Response status is coarse and only includes the status enum, not messages. Tests should cover admin denial, layout version cache value, status conversion, repeated finalization, and error response layout version.
