<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/AbstractReconfigureSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/AbstractReconfigureSubCommand.java

Purpose: Shared base for `ozone admin reconfig` action commands. It decides whether to target one node address or all in-service datanodes, then dispatches the concrete operation.

Important APIs and types: `Callable<Void>`, parent `ReconfigureCommands`, `ExecutorService`, `Executors.newFixedThreadPool(5)`, `ReconfigureSubCommandUtil.parallelExecute`, and abstract `executeCommand(NodeType, String)`.

Control flow: `call()` checks `parent.isBatchReconfigDatanodes()`. Batch mode gets all operable datanode client RPC addresses and runs the concrete operation in parallel. Single-node mode requires `--address`, prints an error and returns if missing, otherwise calls `executeCommand(parent.getService(), parent.getAddress())`.

State and persistence behavior: No persistence. Runtime state is inherited parent options and a batch executor. Remote reconfiguration state is changed only by subclasses.

Dependencies and integration points: Base class for start, status, and properties subcommands. Depends on the parent command for service/address/batch selection.

Risks: Batch mode always uses datanode node type in the utility, regardless of the parent `--service` value. Missing address prints an error without non-zero exception. The executor size and timeout are fixed in utility code.

Test signals: Cover missing address, single OM/SCM/DATANODE dispatch, batch datanode address collection, and exception behavior from subclass operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/AbstractReconfigureSubCommand.java -->
