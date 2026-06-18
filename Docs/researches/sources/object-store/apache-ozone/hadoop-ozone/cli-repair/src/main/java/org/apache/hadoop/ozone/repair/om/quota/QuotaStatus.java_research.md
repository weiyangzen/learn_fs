## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/QuotaStatus.java

Purpose: read-only command that prints the status of the last OM quota repair run.

Important APIs and control flow: picocli options accept optional `--service-id`/`--om-service-id` and `--service-host`. As a child of `QuotaRepair`, `call` opens an OM protocol client with `forceHA=false`, invokes `getQuotaRepairStatus()`, prints the response to stdout, and closes the client.

State and dependencies: no state mutation. It depends on `QuotaRepair.createOmClient`, `OzoneManagerProtocol`, and `ReadOnlyCommand` marker semantics.

Risks and test signals: because it implements `ReadOnlyCommand`, it is exempt from the repair CLI dry-run requirement. Incorrect host/service selection can read from an unintended OM. `TestOzoneRepair.subcommandsSupportDryRun` specifically permits leaf commands that implement `ReadOnlyCommand`.
