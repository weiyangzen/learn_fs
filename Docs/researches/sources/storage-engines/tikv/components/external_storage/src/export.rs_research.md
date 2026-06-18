<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/export.rs -->
# sources/storage-engines/tikv/components/external_storage/src/export.rs

Purpose: this module adapts protobuf `StorageBackend` configurations and provider-specific blob clients into the crate's `ExternalStorage` trait. It also provides helper constructors and a wrapper for encrypted local restore files.

Important APIs and types: `create_storage` dispatches to `create_backend`. `make_s3_backend`, `make_local_backend`, `make_hdfs_backend`, `make_noop_backend`, `make_gcs_backend`, and `make_azblob_backend` build protobuf backend messages. `Compat<Blob>` wraps cloud `BlobStorage + IterableStorage + DeletableStorage` clients and implements `ExternalStorage`. `AutoEncryptLocalRestoredFileExternalStorage<S>` delegates all storage operations but overrides `restore` to create the local output file through an `encryption::DataKeyManager`.

Control flow: `create_backend` matches `StorageBackend_oneof_backend`: local creates `LocalStorage`, HDFS creates `HdfsStorage`, noop creates `NoopStorage`, S3 configures multipart size, GCS optionally selects `gcp_v2`, Azure constructs `AzureStorage`, and unsupported `CloudDynamic` returns an error. Creation latency is recorded through `record_storage_create`.

State and persistence behavior: backend creation mostly builds client objects. `AutoEncryptLocalRestoredFileExternalStorage::restore` mirrors the default restore pipeline: read full/range object, optionally checksum encrypted bytes, decrypt if needed, decompress if needed, then write through a local encrypted file writer and validate length/checksums.

Dependencies and integration points: it integrates `aws`, `azure`, `gcp`, `gcp_v2`, `cloud::blob`, `kvproto::brpb`, `DataKeyManager`, and crate-level helpers such as `compression_reader_dispatcher`, `encrypt_wrap_reader`, and `read_external_storage_into_file`.

Risks: unsupported or missing backend variants return generic `NotFound` errors. GCS v1/v2 selection is a config flag, so behavior can diverge across deployments. The encrypted restore wrapper duplicates much of the default restore logic, so future restore-pipeline changes must be applied in both places.

Test signals: `test_create_storage` verifies local path errors, valid local storage creation, noop creation, and invalid empty backends. Provider-specific creation is not exercised here.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/export.rs -->
