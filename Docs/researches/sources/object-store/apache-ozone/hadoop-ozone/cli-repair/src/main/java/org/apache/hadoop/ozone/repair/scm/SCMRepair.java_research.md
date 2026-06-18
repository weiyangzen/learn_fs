## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/SCMRepair.java

Purpose: top-level `ozone repair scm` command container for Storage Container Manager repair utilities.

Important APIs and control flow: picocli registers `CertRepair` and shared `TransactionInfoRepair` under `scm`. `@MetaInfServices(RepairSubcommand.class)` publishes this provider to the global repair CLI.

State and dependencies: no direct state or persistence. It integrates SCM-specific repairs with service-loader command discovery.

Risks and test signals: registration errors would hide certificate recovery or SCM transaction repair. `TestTransactionInfoRepair` exercises the `scm update-transaction` path through the global CLI, and `TestOzoneRepair` validates dry-run metadata policy.
