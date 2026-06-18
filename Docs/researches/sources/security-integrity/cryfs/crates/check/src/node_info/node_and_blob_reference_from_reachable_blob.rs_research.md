# sources/security-integrity/cryfs/crates/check/src/node_info/node_and_blob_reference_from_reachable_blob.rs

Purpose: This struct carries node reference context while traversing nodes of a blob known to be reachable from the filesystem root.

Important APIs and flow: It contains `node_info: NodeReference` and `blob_info: BlobReferenceWithId`.

State and persistence: It is transient traversal state passed through runner recursion and converted into `NodeAndBlobReference` for diagnostic storage.

Dependencies and integration: It is used by `RecoverRunner`, `CheckUnreferencedNodes`, and `CheckParentPointers` callback signatures through `FilesystemCheck`.

Risks and test signals: The type assumes root reachability. Unreachable-node scans use `MaybeBlobReferenceWithId::UnreachableFromFilesystemRoot` instead of this type.
