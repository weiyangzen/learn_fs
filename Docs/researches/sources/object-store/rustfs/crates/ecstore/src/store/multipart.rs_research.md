# sources/object-store/rustfs/crates/ecstore/src/store/multipart.rs

## Purpose
This file implements `ECStore` multipart-upload handlers. It validates multipart arguments, routes operations to the correct erasure pool, handles multi-pool lookup by skipping suspended pools and invalid upload IDs, chooses a pool for new uploads, and delegates part/list/abort/complete operations to `Sets`.

## Important APIs, Types, And Functions
- `handle_list_object_parts` validates list-parts input, then finds the pool containing the upload ID.
- `handle_list_multipart_uploads` validates list-multipart input and merges uploads from all non-suspended pools in multi-pool deployments.
- `handle_new_multipart_upload` and `handle_new_multipart_upload_with_pool_idx` create a new upload and return the selected pool index for callers that need it.
- `handle_put_object_part`, `handle_get_multipart_info`, `handle_abort_multipart_upload`, and `handle_complete_multipart_upload` scan pools until the upload ID is found, returning the first non-invalid-upload error.
- `handle_copy_object_part` is present but returns `StorageError::NotImplemented`.

## Control Flow
All handlers short-circuit to `self.pools[0]` for single-pool deployments. In multi-pool mode:
- Read/update operations over an existing upload iterate pools in order, skip suspended pools, and treat `InvalidUploadID` as "try the next pool".
- Non-`InvalidUploadID` errors are returned immediately so real disk/quorum failures are not hidden.
- If no pool has the upload, handlers return `StorageError::InvalidUploadID(bucket, object, upload_id)`.
- `handle_list_multipart_uploads` is different: it queries all non-suspended pools and concatenates upload entries into one `ListMultipartsInfo`.
- `handle_new_multipart_upload_with_pool_idx` first looks for existing uploads for the same object in non-suspended, non-rebalancing pools and creates the new upload in that pool if found. Otherwise it calls `get_pool_idx` to select a target by object key and capacity. During data movement it rejects creating a target upload in the source pool.

## State And Persistence Behavior
Persistent multipart state lives in pool/set implementations. This file controls which pool receives mutations:
- New uploads create upload metadata in one selected pool.
- `put_object_part` stores part data in the pool owning the upload ID.
- Abort removes upload state in the owning pool.
- Complete finalizes multipart state into an object via the owning pool.
- List operations aggregate transient metadata views and do not persist state.

## Dependencies And Integration Points
The module depends on argument checkers such as `check_list_parts_args`, multipart result types, `ObjectOptions`, `PutObjReader`, pool suspension/rebalance state, upload ID error classifiers, `MAX_UPLOADS_LIST`, and pool selection methods from `rebalance.rs`. It integrates S3 multipart APIs with erasure pool placement and data movement safeguards.

## Risks And Edge Cases
- Namespace locking is marked TODO for list parts and not implemented locally for other multipart operations; correctness depends on lower-level pool/set locking.
- `handle_list_multipart_uploads` concatenates uploads from all pools but does not sort, truncate, deduplicate, or compute continuation state across pools, which can affect S3 marker semantics in multi-pool deployments.
- `handle_new_multipart_upload_with_pool_idx` calls `list_multipart_uploads(bucket, object, ...)` using the object as prefix to detect existing uploads; broad prefix matching could be surprising if lower layers do not enforce exact object matching.
- `handle_copy_object_part` is not implemented, so multipart copy workflows relying on UploadPartCopy will fail.
- `handle_put_object_part` passes a single mutable reader through sequential pool attempts; if a pool consumes bytes before returning an `InvalidUploadID`-classified error, later attempts may see a partially consumed stream. The expected lower-layer behavior should be verified.
- Data movement rejects source-pool overwrites only at new-upload selection time; subsequent part/complete paths rely on upload placement.

## Test Signals
No tests are defined in this file. Current signal is through shared error classifiers and higher-level multipart integration tests, if present. High-value tests would cover multi-pool invalid-upload fallback, suspended/rebalancing pool skips, data-movement source-pool rejection, list aggregation ordering/limits, and the unimplemented copy-part API contract.
