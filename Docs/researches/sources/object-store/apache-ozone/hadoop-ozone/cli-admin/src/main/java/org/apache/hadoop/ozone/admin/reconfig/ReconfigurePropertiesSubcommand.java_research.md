<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigurePropertiesSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigurePropertiesSubcommand.java

Purpose: Lists reconfigurable properties for a selected OM, SCM, datanode, or batch of in-service datanodes.

Important APIs and types: `ReconfigureProtocol.getServerName()`, `listReconfigureProperties()`, `ReconfigureSubCommandUtil.getSingleNodeReconfigureProxy`, `HddsProtos.NodeType`, and inherited dispatch from `AbstractReconfigureSubCommand`.

Control flow: For each target, `executeCommand` opens a reconfigure proxy, obtains the server name and property list, prints a header with node address, then prints one property per line. IOExceptions print an address-specific error and are rethrown as RuntimeException.

State and persistence behavior: Read-only. No remote reconfiguration starts; it reads server-declared property metadata.

Dependencies and integration points: Shares proxy creation with reconfig start/status; used for both single-node and batch datanode modes.

Risks: Unlike start/status, this command wraps IOExceptions in RuntimeException, which can affect batch success/failure accounting differently. Output is plain text only.

Test signals: Mock property lists, empty lists, IOException wrapping, server-name header, and batch per-node output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigurePropertiesSubcommand.java -->
