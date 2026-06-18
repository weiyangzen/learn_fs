# sources/object-store/minio/cmd/object-api-deleteobject_test.go

## Purpose
This test file verifies `ObjectLayer.DeleteObject` behavior through the common `ExecObjectLayerTest` harness, so the same behavioral contract is exercised against the supported object layer implementations. The focus is simple object deletion and directory-marker cleanup semantics rather than versioned deletes or replication deletes.

## Important APIs, types, and functions
`TestDeleteObject` delegates to `testDeleteObject`. The test uses `ObjectLayer.MakeBucket`, `ObjectLayer.PutObject`, `ObjectLayer.DeleteObject`, and `ObjectLayer.ListObjects`. Test inputs are encoded in the local `objectUpload` type and a table containing bucket name, objects to upload, target path, and expected remaining objects. Uploads are built with `mustGetPutObjReader` and MD5 values computed from the in-memory content.

## Control flow
For each table case the test creates a fresh bucket, uploads all objects, deletes one path, lists the bucket, and compares the resulting object names to the expected ordered list. Delete errors are tolerated only when `isErrObjectNotFound` is true; all other errors fail the case. The cases cover deleting a normal object, deleting a child that leaves its parent directory empty, deleting one child while a sibling remains, attempting to delete a non-empty directory marker, and deleting an explicit empty directory object.

## State and persistence behavior
The test mutates real object-layer state in temporary test backends: buckets are created, object data is persisted through `PutObject`, and delete operations must update the persisted namespace seen by subsequent `ListObjects`. It indirectly verifies cleanup of synthetic/empty directory entries when the last child is removed, while preserving directory-like prefixes that still have contents.

## Dependencies and integration points
The test depends on the object-layer test harness, object reader helpers, MD5/hex encoding, and `isErrObjectNotFound` from the object API error helpers. It integrates with listing semantics because deletion correctness is asserted through `ListObjects`, not through filesystem inspection.

## Risks and test signals
The main regression signal is namespace drift after deletes: accidental removal of siblings, failure to remove explicit empty directory objects, or incorrectly deleting non-empty directory prefixes. The test is intentionally small and does not cover versioned deletes, object lock, delete-marker replication, prefix-forced deletes, or multi-delete batch behavior.
