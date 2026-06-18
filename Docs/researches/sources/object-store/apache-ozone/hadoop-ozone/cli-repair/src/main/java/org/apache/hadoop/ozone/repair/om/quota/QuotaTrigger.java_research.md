## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/QuotaTrigger.java

Purpose: online repair command that asks a running OM to start quota repair for all buckets or a specified bucket list.

Important APIs and control flow: accepts optional service selection arguments and `--buckets` as comma-separated `/<volume>/<bucket>` URIs. `execute` parses the list, opens an OM client via the parent `QuotaRepair`, logs the target scope, and unless dry-run calls `startQuotaRepair(bucketList)` followed by `getQuotaRepairStatus()`.

State and dependencies: state mutation happens in OM via RPC; the CLI does not edit DB files. Depends on `RepairTool`, `StringUtils`, `OzoneManagerProtocol`, and the shared quota client factory.

Risks and test signals: bucket URI strings are split but not deeply validated in this class, so server-side validation is important. Status printed after start is a snapshot, not completion proof. No direct quota trigger tests in this subset.
