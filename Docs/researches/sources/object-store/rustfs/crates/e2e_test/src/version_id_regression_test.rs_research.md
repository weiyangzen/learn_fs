# sources/object-store/rustfs/crates/e2e_test/src/version_id_regression_test.rs

Purpose: e2e regression coverage for issue #1066, where S3 responses used by Veeam could return missing or empty `version_id` when bucket versioning was enabled.

Important APIs and functions: helpers create clients/buckets and toggle versioning through `put_bucket_versioning` with `Enabled` or `Suspended`. Tests cover `put_object`, `copy_object`, `create_multipart_upload`/`upload_part`/`complete_multipart_upload`, `head`, `list`, and `delete`.

Control flow: enabled-versioning tests assert `version_id.is_some()` and non-empty for put, copy, complete-multipart, and simulated Veeam paths. Suspended-versioning tests assert `version_id == None` for the same write classes. Non-versioned and basic-operation tests guard against broad S3 regressions. A Terraform-style put/delete/put scenario verifies a state object is readable after a delete marker workflow.

State and persistence: each serial test starts a fresh RustFS server, creates a bucket, mutates bucket versioning config, writes object versions/delete markers, and relies on the environment for cleanup.

Dependencies and integration points: uses AWS SDK S3 versioning types, multipart completion types, ByteStream, and `RustFSTestEnvironment`.

Risks: most bucket names are fixed; failed tests can leave colliding state if the harness does not isolate storage. Assertions inspect SDK output fields rather than raw headers, so serialization bugs below the SDK boundary could be missed.

Test signals: strong coverage for versioning response semantics expected by Veeam, suspended behavior, multipart completion, and delete-marker recovery.
