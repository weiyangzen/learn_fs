<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/DeletedBlocksTxnCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/DeletedBlocksTxnCommands.java

Purpose: Picocli grouping command for SCM deleted-block transaction operations. It currently exposes the summary subcommand.

Important APIs and types: Picocli `@Command`, `HddsVersionProvider`, and `GetDeletedBlockSummarySubcommand`.

Control flow: No methods; Picocli routes `ozone admin scm deletedBlocksTxn summary` to the child.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Registered under `ScmAdmin` as the namespace for deleted-block transaction admin commands.

Risks: Passive registration only.

Test signals: CLI help and child command routing should include `summary`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/DeletedBlocksTxnCommands.java -->
