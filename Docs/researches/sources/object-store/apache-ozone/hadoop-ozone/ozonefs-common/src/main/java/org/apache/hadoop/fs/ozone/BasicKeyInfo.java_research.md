<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicKeyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicKeyInfo.java

Purpose: minimal Ozone key metadata DTO used by filesystem adapter iterators without exposing broader Ozone client classes across classloader boundaries.

Important APIs and functions: constructor `BasicKeyInfo(String name, long modificationTime, long size)` and getters `getName`, `getModificationTime`, and `getDataSize`.

Control flow: construction assigns immutable-by-convention private fields; getters return stored values. There are no setters, validation, equality, or serialization methods.

State and persistence behavior: in-memory value object only. It carries key name, modification time, and data size from `OzoneKey` into listing/rename/delete logic.

Dependencies and integration: intentionally depends only on primitive Java types and `String`. Integrated by `BasicOzoneClientAdapterImpl.IteratorAdapter`, `BasicRootedOzoneClientAdapterImpl.IteratorAdapter`, and `BasicOzoneFileSystem.OzoneListingIterator`. Risks are low, but mutable non-final fields and lack of null/negative validation leave correctness to callers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicKeyInfo.java -->
