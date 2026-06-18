<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/DBHandle.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/DBHandle.java

Purpose: abstract closeable holder for a container metadata DB store and its path.

Important APIs and control flow: constructor captures `DatanodeStore` and container DB path. Getters expose both. `cleanup` defaults to true and can be overridden by concrete handles. It implements Ratis `UncheckedAutoCloseable`, leaving close behavior to subclasses.

State and persistence: holds references to a metadata store and DB path; does not itself persist or close. Subclasses own actual resource lifetime.

Dependencies and integration: used by container metadata-store cache/handle code that needs a common DB handle type.

Risks and test signals: concrete implementations should be tested for close idempotency, cleanup semantics, and path/store consistency. The base class returning true for cleanup can hide missing cleanup implementations if callers assume it performed work.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/DBHandle.java -->
