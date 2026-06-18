## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconNamespaceSummaryManager.java

Purpose: `ReconNamespaceSummaryManager` defines DB operations for namespace summary records keyed by object ID.

Important APIs and types: staged-manager creation, `reinitialize`, `clearNSSummaryTable`, deprecated `storeNSSummary`, batch store/delete, direct delete, `getNSSummary`, and `commitBatchOperation`. Value type is `NSSummary`.

Control flow: namespace summary tasks update object summaries through batch APIs during OM event consumption or reprocess. API endpoints read summaries by object ID for namespace views.

State and persistence: implementations persist NSSummary records in Recon RocksDB. Staged managers and clear operations support full rebuilds.

Dependencies and integration points: used by namespace summary tasks and namespace API endpoints for volume/bucket/directory/key aggregation.

Risks and edge cases: stale summaries can remain if delete events are missed or batch delete/store ordering is wrong. The deprecated direct store API suggests callers should prefer batch operations for consistency.

Test signals: the repository has many namespace endpoint tests (`TestNSSummaryEndpoint*`, disk usage ordering tests) that indirectly validate summary persistence. Manager-specific tests should cover staged rebuilds and delete semantics.
