# sources/object-store/rustfs/crates/e2e_test/src/list_objects_duplicates_test.rs

Purpose: End-to-end regression tests for duplicate results in `ListObjectsV2`. The file protects common-prefix de-duplication when explicit directory marker objects exist, and content de-duplication/order when listing below a prefix without a delimiter.

Important APIs/types/functions: It uses `RustFSTestEnvironment`, `init_logging`, AWS SDK S3 `Client`, `ByteStream`, `serial_test::serial`, and `tracing::info`. Helpers include `create_s3_client` and a retrying `create_bucket` that tolerates `BucketAlreadyOwnedByYou` and `BucketAlreadyExists` and retries transient creation failures up to 20 times.

Control flow: `test_list_objects_v2_unique_common_prefixes` creates `folder/file.txt` and a zero-byte `folder/` marker, then lists the bucket with `delimiter("/")`. It filters `result.common_prefixes()` for `folder/` and asserts there is exactly one entry, then asserts the explicit marker is not also exposed in `Contents`. `test_list_objects_v2_unique_contents_with_explicit_directory_markers` creates `marker/`, `marker/subdir/`, `marker/file.txt`, and `marker/subdir/file.txt`, lists with `prefix("marker/")` and no delimiter, collects content keys, and asserts the exact four-key lexicographic sequence and `key_count=4`.

State and persistence behavior: The tests persist real object keys into a temporary RustFS bucket. The first test checks the delimiter projection layer, where raw keys and marker objects collapse into `CommonPrefixes`. The second checks the flat object listing state under a prefix, where marker objects should appear as normal objects when no delimiter is supplied and nested file keys must not be duplicated.

Dependencies and integration points: These tests exercise the RustFS S3 ListObjectsV2 implementation through the AWS SDK, especially the interaction between object-store key iteration, delimiter rollup, prefix filtering, `Contents`, `CommonPrefixes`, and `KeyCount` serialization. They model behavior used by backup tools such as Veeam that create zero-byte slash-ending folder markers.

Risks: The first test encodes a specific interpretation that `folder/` should be represented only as a common prefix when delimiter `/` is supplied, not also as an object. This is compatible with the target regression but should be reviewed if RustFS intentionally changes directory-marker compatibility behavior. The bucket helper retries for server readiness but uses string matching on SDK error text. Fixed bucket names require serialized execution.

Test signals: Signals are one and only one `CommonPrefix` with prefix `folder/`, no `Contents` object keyed `folder/` in delimiter mode, exact `Contents` vector `marker/`, `marker/file.txt`, `marker/subdir/`, `marker/subdir/file.txt`, and `result.key_count() == Some(4)`.
