## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/package-info.java

Purpose: package Javadoc marker for OM quota repair tools.

APIs and integration: no executable code. It documents the package containing the quota command group and its status/start subcommands.

State and dependencies: no runtime state or dependencies.

Risks and test signals: documentation-only file. Command behavior depends on `QuotaRepair`, `QuotaStatus`, and `QuotaTrigger`; dry-run/read-only metadata is indirectly checked by `TestOzoneRepair`.
