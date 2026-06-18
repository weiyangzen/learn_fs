<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/DecommissionScmSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/DecommissionScmSubcommand.java

Purpose: Implements `ozone admin scm decommission`, removing an SCM from the SCM Ratis ring and certificate store through `ScmClient`.

Important APIs and types: `ScmSubcommand`, `ScmClient.decommissionScm`, `DecommissionScmResponseProto`, nested `NodeIdOptions`, and deprecated hidden `-nodeid` alias.

Control flow: `execute()` calls `decommissionScm(nodeId)`. If the response success flag is false, it builds an error message including optional server error text and throws IOException for a non-zero exit. On success it prints `Decommissioned Scm <nodeId>`.

State and persistence behavior: No local persistence. Remote SCM membership/certificate state changes on success.

Dependencies and integration points: Registered below `ScmAdmin`; uses the standard `ScmSubcommand` client lifecycle.

Risks: It trusts the response success flag and optional error message. There is no config preflight comparable to OM decommissioning.

Test signals: Success/failure response handling, error message inclusion, deprecated alias parsing, and exception exit behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/DecommissionScmSubcommand.java -->
