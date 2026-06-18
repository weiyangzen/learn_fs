<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/GetDeletedBlockSummarySubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/GetDeletedBlockSummarySubcommand.java

Purpose: Prints aggregate deleted-block transaction statistics from SCM.

Important APIs and types: `ScmClient.getDeletedBlockSummary()`, `HddsProtos.DeletedBlocksTransactionSummary`, and `ScmSubcommand`.

Control flow: `execute()` fetches the summary. Null produces `DeletedBlocksTransaction summary is not available`; otherwise it prints total transaction count, block count, block size, and replicated block size.

State and persistence behavior: Read-only. It reports SCM metadata/metrics about queued or tracked deleted-block transactions.

Dependencies and integration points: Child of `DeletedBlocksTxnCommands`, using the standard SCM client provided by the admin CLI.

Risks: Plain text output has fixed labels that scripts may parse. Null summary is handled as unavailable rather than an error.

Test signals: Null summary output, all numeric fields, and IOException propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/GetDeletedBlockSummarySubcommand.java -->
