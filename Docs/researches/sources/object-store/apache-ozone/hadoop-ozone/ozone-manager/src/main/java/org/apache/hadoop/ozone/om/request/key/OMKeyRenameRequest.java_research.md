# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyRenameRequest.java

Purpose: `OMKeyRenameRequest` renames a single committed key in legacy/object-store layouts by tombstoning the old key-table row and inserting the same `OmKeyInfo` under a new DB key with updated key name and modification time.

Important APIs and types: The class extends `OMKeyRequest` and uses `RenameKeyRequest`, `RenameKeyResponse`, `KeyArgs`, `OmKeyInfo`, `OMKeyRenameResponse`, key-table cache entries, bucket locks, ACL checks for DELETE on the source and CREATE on the destination, and an old-client bucket-layout validator.

Control flow: `preExecute` validates destination key characters, extracts source and destination names, stamps modification time, resolves bucket links, checks source delete and destination create ACLs, writes normalized values back into the request, and attaches user info. `validateAndUpdateCache` rejects empty names, acquires the bucket lock, validates volume/bucket, computes source and destination ozone keys, rejects an existing destination, loads the source key, updates its transaction ID, key name, and modification time, tombstones the source key-table entry, inserts the destination cache entry, returns an `OMKeyRenameResponse`, audits the operation, and updates metrics on failure.

State and persistence behavior: The operation mutates only key-table cache entries: old DB key tombstone plus new DB key value. Bucket quota and namespace do not change. The `OmKeyInfo` object retains its object ID, blocks, replication, ACLs, owner, and versions, but its logical key name and update ID change. Open keys are not supported for rename.

Dependencies and integration points: It depends on OM metadata key naming, bucket locks, ACL infrastructure, audit and metrics, response-side batch updates, and validation framework support for old clients and non-legacy bucket layouts. FSO behavior is implemented separately because directories and parent object IDs require different semantics.

Risks: The method does not normalize destination path beyond `extractDstKey` in this base class, so path semantics are simple object-key semantics. There is no overwrite behavior; existing destination always fails. Renaming an open key is explicitly unsupported. The source `OmKeyInfo` is modified in place after rebuilding, so tests should guard against unintended aliasing with cached values.

Test signals: `TestOMKeyRenameRequest` and `TestOMKeyRenameResponse` should verify source tombstone and destination insertion, destination-exists failure, source-missing failure, empty-name rejection, key name/modification/update ID updates, unchanged quota, ACL checks for both paths, audit map source/destination fields, and old-client layout validation.
