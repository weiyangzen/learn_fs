<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/TransferScmLeaderSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/TransferScmLeaderSubCommand.java

Purpose: Manually transfers SCM Ratis leadership to a specified SCM UUID or a random follower.

Important APIs and types: `ScmOption.createScmClient`, `ScmClient.transferLeadership`, parent `ScmAdmin`, Picocli `ArgGroup`, and nested `TransferOption`.

Control flow: `call()` creates an SCM client from root config, converts random mode to an empty SCM ID, invokes `transferLeadership`, and prints a success message naming random or explicit target.

State and persistence behavior: No local persistence. Remote SCM Ratis leadership changes if accepted.

Dependencies and integration points: Uses `ScmOption` instead of `ScmSubcommand`, and is registered below `ScmAdmin`.

Risks: The created client is not wrapped in try-with-resources in this method. Empty-string random sentinel must stay aligned with server semantics. There is no post-transfer verification.

Test signals: Arg-group exclusivity, random/explicit target RPC values, client creation from config, and success output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/TransferScmLeaderSubCommand.java -->
