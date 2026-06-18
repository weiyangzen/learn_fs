# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotObjectStore.java

Purpose: This concrete subclass runs the shared snapshot suite for `OBJECT_STORE` bucket layout. It covers snapshot behavior when keys are treated as object-store keys rather than FSO directory/file entries.

Important APIs/types/functions: The class extends `TestOmSnapshot`, imports `BucketLayout.OBJECT_STORE`, and calls `super(OBJECT_STORE, false, false, false, false)`.

Control flow: The inherited suite builds a MiniOzoneCluster with object-store bucket layout, native diff enabled if libraries load, filesystem paths disabled, and no linked buckets. Object-store-specific behavior appears in inherited conditional assertions, such as directory entries and filesystem API assumptions.

State and persistence behavior: Snapshot state is stored and diffed through the object-store key table. Directory-like names are treated differently from FSO, and inherited tests account for ordering and missing explicit directory entries.

Dependencies and integration points: This subclass integrates object-store bucket layout with snapshot create/read/list/delete/diff, RocksDB key table SST filtering, object tag and metadata modification, stream key APIs, and MPU lifecycle tests.

Risks and edge cases: Filesystem-specific tests are skipped where object-store semantics do not support them. Directory ordering and rename semantics differ from FSO, so inherited assertions branch on bucket layout. Constructor-only drift would change the entire object-store matrix.

Test signals: Passing inherited assertions demonstrate that object-store snapshots preserve data, produce expected diff entries, reject invalid operations, and handle restart/deletion/MPU/tag cases.
