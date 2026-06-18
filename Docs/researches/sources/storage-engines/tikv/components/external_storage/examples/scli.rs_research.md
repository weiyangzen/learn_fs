<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/examples/scli.rs -->
# sources/storage-engines/tikv/components/external_storage/examples/scli.rs

Purpose: this example implements `scli`, a small command-line tool for saving a local file to an external storage backend or loading an object back to a local file. It demonstrates the public `external_storage` construction and read/write APIs.

Important APIs and functions: `Opt` defines CLI flags for backend type, local file, remote name, local/HDFS path, credential file, endpoint, region, bucket, prefix, and subcommand. `StorageType` supports `Noop`, `Local`, `Hdfs`, `S3`, `GCS`, and `Azure`. Helper functions build protobuf `StorageBackend` values: `create_s3_storage`, `create_gcs_storage`, and `create_azure_storage` parse flags and optional INI/JSON credential data. `process` selects a backend, calls `create_storage`, then dispatches `Save` or `Load`.

Control flow: for save, it opens the local file, gets metadata length, wraps it with `AllowStdIo`, and calls `storage.write` through `block_on_external_io`. For load, it calls `storage.read`, creates the local output file, starts a Tokio runtime, and copies the async reader into the blocking file wrapper.

State and persistence behavior: save persists remote objects or local-storage files; load overwrites/creates the local file. Credentials are read from disk but not persisted. Errors are printed by `main` instead of returned with process-specific exit handling.

Dependencies and integration points: it integrates `structopt`, `rust-ini`, BR protobuf backend messages, `futures_util::copy`, `tokio::Runtime`, and the crate's backend helper constructors. It is an example, not a production CLI.

Risks: `opt.path.unwrap()` is used for local and HDFS storage, so missing path panics rather than producing a clean error. S3 requires region and bucket, while GCS/Azure require bucket. Credential parsing assumes a `default` INI section with specific key names. The load path uses `storage.read` directly, so HDFS, whose read is unimplemented, is not usable for load.

Test signals: no tests exist in the example. Its value is compile-time example coverage and manual smoke testing.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/examples/scli.rs -->
