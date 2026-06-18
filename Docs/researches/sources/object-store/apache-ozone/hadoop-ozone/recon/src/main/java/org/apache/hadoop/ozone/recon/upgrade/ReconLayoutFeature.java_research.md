# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconLayoutFeature.java

Purpose: `ReconLayoutFeature` enumerates Recon metadata layout versions and binds optional upgrade actions to each feature.

Important APIs and types: features currently include versions 0 through 5: initial layout, task status statistics, unhealthy container replica mismatch, NSSummary aggregated totals, replicated file sizes, and unhealthy container state/container id index. Each enum stores version, description, and optional `ReconUpgradeAction`. `addAction` keeps the first action. `registerUpgradeActions` scans `org.apache.hadoop.ozone.recon.upgrade` for `@UpgradeActionRecon`, instantiates actions, and attaches them. `determineSLV` returns the max feature version.

Control flow and integration: `ReconLayoutVersionManager` calls `registerUpgradeActions` at construction and later finalizes features with version greater than current MLV.

State and persistence: action references are stored in enum instances for the JVM process. Version persistence is handled by schema version table manager elsewhere.

Dependencies: Reflections library and the local upgrade action annotation/interface.

Risks and test signals: reflection registration can fail at runtime if action constructors change. Duplicate actions for a feature are silently ignored after the first. Tests should cover action registration, SLV computation, duplicate behavior, and ordering by version in the manager.
