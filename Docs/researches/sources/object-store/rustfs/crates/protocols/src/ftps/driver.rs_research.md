# sources/object-store/rustfs/crates/protocols/src/ftps/driver.rs

Purpose: This module adapts libunftp's storage interface to the S3-compatible `StorageBackend`, presenting buckets and objects as an FTP filesystem.

Important APIs and types: `FtpsMetadata` implements unftp `Metadata` with size, optional modified time, directory flag, uid/gid zero, and no symlink support. `FtpsDriver<S>` wraps a generic S3 backend. Helper methods include `new`, `list_buckets`, `parse_s3_path`, and `delete_bucket_recursively`. The `StorageBackend<FtpsUser>` implementation supplies `metadata`, `list`, `get`, `put`, `del`, `mkd`, `rmd`, `cwd`, and `rename`.

Control flow: Paths are cleaned and split into bucket/object with `rustfs_utils::path`. Root listing calls `ListBuckets`; bucket paths call `HeadBucket`; object paths call `HeadObject`, `GetObject`, `PutObject`, or `DeleteObject`. Directory listing uses `ListObjectsV2` with delimiter `/`, converts `contents` into files, and `common_prefixes` into directories. `get` fully drains the S3 body into a `Vec<u8>` and returns a cursor. `put` rejects append (`start_pos > 0`), copies the whole reader into memory, and performs one `PutObject`. Bucket removal pages through all objects, deletes them one by one, then deletes the bucket. `rename` is explicitly unsupported.

State and persistence behavior: The driver is stateless aside from the backend handle. Persistent effects are S3 bucket creation/deletion, object uploads/deletes, and recursive object deletion during bucket removal. It does not store local handles or cache metadata. PUT and GET buffer whole object bodies in memory.

Dependencies and integration points: It integrates unftp storage traits, `s3s::dto` builders, `authorize_operation`, `S3Action`, `FtpsUser.session_context`, `MaskedAccessKey` logging, and RustFS path helpers. It relies on the session's IAM-derived access and secret keys for every backend call.

Risks: `mkd` creates buckets without an explicit `authorize_operation` call in this file, unlike most other mutating operations. Whole-object buffering in `get` and `put` can be unsafe for large files. Recursive bucket deletion ignores individual object delete errors and can leave partial cleanup before bucket delete. `del` only treats a path ending in `/` as bucket deletion, while `rmd` always treats the parsed bucket as the target. S3 pseudo-directories below a bucket are not first-class for FTPS creation/removal.

Test signals: There are no local tests in this file. Expected signals are authorization denial mapping to unftp errors, root and bucket listings, metadata conversion from S3 timestamps/content lengths, append rejection, put size return, recursive deletion pagination, idempotent no-such-bucket handling, and rename returning `CommandNotImplemented`.
