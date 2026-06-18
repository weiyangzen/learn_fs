# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/DeletedBlockLogStateManagerInvoker.java

Purpose: Generated HA invoker for replicated deleted-block transaction table mutations.

Important APIs and types: `ReplicateMethod` includes overloaded `addTransactionsToDB` and `removeTransactionsFromDB`, with optional `DeletedBlocksTransactionSummary`. Local methods include read-only iterator, `onFlush`, and `reinitialize`.

Control flow: Proxy write methods call `invokeReplicateDirect` with either one or two arguments. `invokeLocal` collapses overloads by checking argument length, applies the mutation to the underlying `DeletedBlockLogStateManager`, and returns `Message.EMPTY` for void paths.

State and persistence behavior: Mutations affect the deleted blocks transaction table and stateful service config table through the underlying manager; `onFlush` lets the local manager react to DB buffer flushes.

Dependencies and integration points: Used by SCM block manager/deleted block log, checkpoint reload, and HA request serialization for `ArrayList` and protobuf summary values.

Risks and test signals: Raw `ArrayList` element typing relies on list codec support and homogeneous elements. Tests should cover both overloads, remove/add replication, iterator pass-through, `onFlush`, and table reinitialize after checkpoint install.
