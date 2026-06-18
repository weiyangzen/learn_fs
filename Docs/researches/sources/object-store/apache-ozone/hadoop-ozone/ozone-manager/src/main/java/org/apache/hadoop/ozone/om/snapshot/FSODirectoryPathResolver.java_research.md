# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/FSODirectoryPathResolver.java

Purpose: `FSODirectoryPathResolver` resolves absolute bucket-relative paths for FSO directory object IDs. It implements `ObjectPathResolver` for directory metadata stored in OM's FSO directory table.

Important APIs and types: the constructor takes a table key prefix, bucket object ID, and `Table<String, OmDirectoryInfo>`. The primary API is `getAbsolutePathForObjectIDs(Optional<Set<Long>>, boolean)`, which returns `Map<Long, Path>` and can either skip unresolved IDs or fail fast.

Control flow: the resolver copies the requested object IDs into a mutable set, seeds a breadth-first traversal with the bucket root pair `(bucketId, ROOT_PATH)`, and records the root path if requested. While there are queued parents and unresolved IDs, it opens a table iterator at `prefix + parentObjectId + OM_KEY_PREFIX`, treats returned `OmDirectoryInfo` values as children, resolves child paths by appending child names to the parent path, records requested IDs, and enqueues every child for further traversal.

State and persistence behavior: the class is stateless apart from constructor fields. It reads the directory table with prefix iterators and does not mutate metadata. The returned paths are derived from table contents at read time.

Dependencies and integration points: it depends on OM key prefix conventions, `OmDirectoryInfo` object IDs/names, Apache Commons `Pair`, Guava `Sets`, and the `ObjectPathResolver` interface. Snapshot diff and reclaimable-object code can use it to present FSO directory IDs as paths.

Risks: traversal breadth is limited only by table contents and requested IDs; large unresolved sets may walk large directory subtrees. Iterator prefix correctness depends on the provided `prefix` matching the bucket's directory table key layout. If `skipUnresolvedObjs` is false, stale or cross-bucket IDs cause `IllegalArgumentException`.

Test signals: `TestFSODirectoryPathResolver` covers path resolution behavior, including root and nested directories.
