<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/BlockIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/BlockIterator.java

Purpose: closeable abstraction for iterating blocks inside a container type.

Important APIs and control flow: implementers expose `hasNext`, positioning methods `seekToFirst` and `seekToLast`, and `nextBlock`, which returns the next block or throws `NoSuchElementException`/`IOException` when appropriate. Extending `Closeable` makes resource cleanup part of the contract.

State and persistence: interface only. Implementations usually wrap metadata DB iterators and therefore carry cursor state and open resources.

Dependencies and integration: used by container implementations and block listing/scanning/deletion logic that should not depend on a concrete metadata store.

Risks and test signals: implementation tests should cover cursor movement, empty stores, resource closure, IO exceptions, and whether `nextBlock` returns null or throws at end according to the implementation's documented behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/BlockIterator.java -->
