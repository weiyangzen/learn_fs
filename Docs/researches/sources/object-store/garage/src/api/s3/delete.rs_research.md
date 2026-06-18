# sources/object-store/garage/src/api/s3/delete.rs

## Purpose
Implements object deletion and multi-object deletion. Garage does not remove object data synchronously here; it appends a delete-marker object version so readers see the key as absent while background/version/block cleanup can proceed separately.

## Important APIs, Types, And Functions
`handle_delete_internal` performs the object-table mutation and returns the deleted version UUID and delete-marker UUID. `handle_delete` wraps it with S3 single-delete semantics, returning 204 even if the key did not exist. `handle_delete_objects` parses S3 delete XML, deletes each requested key independently, and returns `DeleteResult` entries unless quiet mode is enabled. `parse_delete_objects_xml` accepts formatted XML while rejecting non-whitespace stray text.

## Control Flow
Internal delete fetches the object from `object_table`, computes a monotonic timestamp with `next_timestamp`, generates a delete marker UUID, identifies the latest non-aborted version as the deleted version, and inserts a new object containing a complete `DeleteMarker` version. Multi-delete collects the body, parses XML using `roxmltree`, iterates objects, calls the same internal delete path, and accumulates per-key success or error XML.

## State And Persistence
Persistence is limited to `object_table.insert(Object::new(bucket_id, key, vec![delete_marker_version]))`. Existing version data, version table rows, block refs, and blocks are not modified here. Delete markers become part of object version history and are interpreted by GET/list filters elsewhere.

## Dependencies And Integration Points
Depends on the S3 object table types, `put::next_timestamp`, S3 XML response structs, and common helpers for body collection. It integrates with GET and LIST through `ObjectVersionState::Complete(ObjectVersionData::DeleteMarker)`, which those modules treat as missing data.

## Risks And Test Signals
Main risks are S3 compatibility for versioned deletion semantics and XML parsing strictness. `version_id` is accepted by the router but ignored by this implementation, so version-specific delete is not implemented here. Tests cover formatted XML, compact XML, quiet parsing, and rejection of non-whitespace text nodes.
