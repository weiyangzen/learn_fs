<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java

## Purpose
Hadoop 2 `AbstractFileSystem` adapter for the bucket-scoped `o3fs` scheme.

## Important APIs, types, and functions
Extends `DelegateToFileSystem`. Constructor delegates to a new Hadoop 2-compatible `OzoneFileSystem` with scheme `o3fs` and no authority requirement. `getUriDefaultPort` returns `-1`; `finalize` closes the wrapped filesystem.

## Control flow
All FileContext operations are delegated through `DelegateToFileSystem` to `OzoneFileSystem`.

## State and persistence behavior
Local state lives in the delegate superclass. Durable state is whatever the underlying filesystem mutates.

## Dependencies and integration points
Provides FileContext API support for Hadoop 2 users of `o3fs`.

## Risks and test signals
Use of `finalize` is lifecycle-fragile and not deterministic. Tests should instantiate through FileContext and verify basic create/list/open/delete behavior and URI default port semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java -->
