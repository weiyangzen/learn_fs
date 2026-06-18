<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureStartSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureStartSubcommand.java

Purpose: Starts an asynchronous reconfiguration task on selected server nodes.

Important APIs and types: `ReconfigureProtocol.startReconfigure()`, `getServerName()`, `ReconfigureSubCommandUtil.getSingleNodeReconfigureProxy`, and inherited target dispatch.

Control flow: `executeCommand` opens the proxy, gets the server name, calls `startReconfigure`, and prints a started message. IOExceptions are caught, an address-specific message and stack trace are printed to stdout, and no exception is rethrown.

State and persistence behavior: No local persistence. Remote servers may start background reconfiguration tasks that later modify runtime configuration values.

Dependencies and integration points: Works for OM, SCM, and DATANODE single-node modes and datanode batch mode through the base command.

Risks: Because IOException is swallowed after printing, callers may see a zero exit for single-node failures. Batch utility may also count such handled failures as successful because no exception escapes.

Test signals: Verify start RPC, server-name output, IOException stack trace output, proxy closure, and batch counting behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureStartSubcommand.java -->
