<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DeletedContainerBlocksSummary.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DeletedContainerBlocksSummary.java

Purpose: reporting helper that summarizes a batch of `DeletedBlocksTransaction` entries for logging and metrics around block deletion.

Important APIs and control flow: `getFrom` wraps a list in a private constructor. Construction iterates every transaction, records transaction ID to retry count, counts transactions whose retry count is positive, aggregates local block counts by container ID, and records total block count. Public accessors expose transaction count, block count, retry transaction count, container count, comma-separated transaction IDs, and a compact `txId(count)` summary. `toString` expands each transaction with tx ID, processed count, container ID, and local IDs.

State and persistence: all state is in-memory and derived from the provided transaction list. There is no defensive copy of `blocks`, so later mutations to the list or protobuf objects can affect `toString` semantics.

Dependencies and integration: used by deletion paths to make SCM delete transaction batches human-readable. Depends on Guava `Maps`, protobuf `DeletedBlocksTransaction`, streams, and Hadoop `StringUtils`.

Risks and test signals: transaction ID ordering is based on hash-map key iteration and should not be treated as stable. Tests should cover duplicate container IDs, retry counts, empty batches, duplicated transaction IDs, and string rendering of local ID lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DeletedContainerBlocksSummary.java -->
