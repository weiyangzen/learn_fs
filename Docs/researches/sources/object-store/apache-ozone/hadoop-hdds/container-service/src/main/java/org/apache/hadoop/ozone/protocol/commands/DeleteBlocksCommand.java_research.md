# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/DeleteBlocksCommand.java

Purpose: SCM command instructing a datanode to delete blocks represented by one or more deleted-block transactions.

Important APIs and functions: constructors accept transaction lists and optionally restore command ID for protobuf conversion. `blocksTobeDeleted` returns the list. `getType` returns `deleteBlocksCommand`. `getProto` serializes command ID and all transactions. `getFromProtobuf` restores from `DeleteBlocksCommandProto`. `toString` emits transaction IDs, container IDs, local ID counts, and counts.

Control flow and state: the transaction list is stored directly and can be mutable depending on caller list.

Dependencies and integration: sent by SCM based on deleted-block log processing and acknowledged through `DeleteBlockCommandStatus`.

Risks and test signals: mutable transaction lists and large diagnostic strings are notable. Tests should cover empty and multi-transaction round trips, command ID preservation, toString formatting without trailing separators, and list mutation expectations.
