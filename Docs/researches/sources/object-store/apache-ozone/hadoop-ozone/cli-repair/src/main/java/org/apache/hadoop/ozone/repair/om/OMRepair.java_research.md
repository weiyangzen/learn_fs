## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/OMRepair.java

Purpose: top-level `ozone repair om` command container for Ozone Manager repair operations.

Important APIs and control flow: picocli registers `FSORepairTool`, `SnapshotRepair`, `TransactionInfoRepair`, `QuotaRepair`, `CompactOMDB`, and `OMRatisLogRepair`. `@MetaInfServices(RepairSubcommand.class)` publishes this command to the repair CLI discovery path.

State and dependencies: no direct persistence. It defines the integration point between the global `OzoneRepair` command and OM-specific repair implementations, including both offline DB mutation tools and online RPC tools.

Risks and test signals: incorrect registration would hide or misplace critical repair tools. `TestOzoneRepair` recursively validates command metadata and dry-run support policy for leaf commands.
