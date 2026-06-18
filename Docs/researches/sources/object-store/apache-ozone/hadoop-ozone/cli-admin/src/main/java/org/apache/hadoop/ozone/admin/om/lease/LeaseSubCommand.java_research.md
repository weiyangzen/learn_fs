<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/LeaseSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/LeaseSubCommand.java

Purpose: Picocli grouping command for OM lease operations. Its current role is to expose the `recover` subcommand.

Important APIs and types: Picocli `@Command`, `LeaseRecoverer`, and command metadata.

Control flow: The class has no methods; Picocli routes `ozone admin om lease recover` to `LeaseRecoverer`.

State and persistence behavior: No state or persistence in the grouping class.

Dependencies and integration points: Registered in `OMAdmin` and provides the namespace for future lease admin subcommands.

Risks: As a passive grouping class, behavior depends entirely on Picocli registration and child command implementations.

Test signals: CLI help/subcommand discovery should include `recover`, and routing should instantiate `LeaseRecoverer` for recover invocations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/LeaseSubCommand.java -->
