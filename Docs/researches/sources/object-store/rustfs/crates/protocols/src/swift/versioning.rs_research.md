# sources/object-store/rustfs/crates/protocols/src/swift/versioning.rs

Implements Swift object version archival and restore logic. Version-enabled containers archive overwritten or deleted current objects into a separate archive container using inverted timestamp keys, and deletes can restore the newest archived version.

Important API surface: `generate_version_name()` creates `{inverted_timestamp}/{container}/{object}` names. `archive_current_version()` checks whether the current object exists and copies it to the archive container. `restore_previous_version()` lists versions, copies the newest back, and deletes the restored archive entry. `list_object_versions()` lists archive objects and filters by `/{container}/{object}` suffix.

Control flow: archive logs start, `head_object`s the current object, skips not-found, maps Swift account/container/object names to S3 bucket/key names, resolves the global object store, gets source object info, and performs storage `copy_object`. Restore lists matching versions, selects the first sorted entry, maps buckets/keys, copies archive to current, then deletes the archive object. Listing validates account, lists up to 1000 archive objects without prefix, converts S3 names back to Swift names, filters suffixes, and sorts ascending so inverted timestamps put newest first.

Persistent state is ordinary objects in an archive container. Current-object data remains in the primary container. Container versioning configuration itself is managed in `container.rs`. Dependencies include Swift account validation, container/object mappers, object HEAD, `resolve_object_store_handle`, storage operations, credentials, and tracing. The Swift handler calls archive before overwrites/deletes and restore after versioned deletes.

Risks: `generate_version_name()` uses `as_secs_f64`; formatting to nanosecond precision may imply more precision than the float preserves. Listing scans only the first 1000 archive objects and filters client-side. Restore reports cleanup failure as an error after the current object was already restored. Copy/restore are not transactional across objects.

Tests cover version name shape, ordering, special characters, filtering logic, and timestamp uniqueness. Storage-integrated archive/restore/list operations are not fully mocked in this file.
