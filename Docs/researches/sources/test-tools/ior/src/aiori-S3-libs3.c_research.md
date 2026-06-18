# sources/test-tools/ior/src/aiori-S3-libs3.c

## Purpose
Implements the `S3-libs3` IOR backend using the newer libs3 API. It maps files and directories to S3 buckets and objects, with a mode for one bucket per file/directory or a shared bucket containing object fragments.

## Important APIs, Types, And Functions
Defines `s3_options_t`, `S3_fd_t`, `data_handling`, and `s3_delete_req`. Registers `S3_libS3_aiori`. Main functions include `S3_options`, `def_file_name`, `def_bucket_name`, libs3 response callbacks, `S3_Create`, `S3_Open`, `S3_Xfer`, `S3_Delete`, `S3_mkdir`, `S3_rmdir`, `S3_stat`, `S3_access`, `S3_GetFileSize`, `S3_check_params`, `S3_init`, and `S3_final`.

## Control Flow
Options establish bucket naming, host/credentials, region/location, SSL, and S3-compatible behavior. Initialization optionally splits a host list by rank, initializes libs3, derives a bucket suffix from the access key, initializes `S3BucketContext`, and creates the shared bucket on rank 0. Create creates a bucket or zero-length object marker. Transfers write each IOR transfer as a separate object key based on file name, offset, and length, or read the matching object. Delete removes a per-file bucket or deletes the base object and matching fragments. Finalization deletes the shared bucket on rank 0 and deinitializes libs3.

## State And Persistence Behavior
Backend state lives in `s3_options_t`, including mutable `bucket_context`, selected host, and generated bucket prefix. File handles store the normalized object name. Data is persisted as many S3 objects when offsets are nonzero. Directory operations are represented by buckets or zero-length objects, not hierarchical filesystem metadata. Global `s3status` and `s3error` capture latest libs3 callback status.

## Dependencies And Integration Points
Uses libs3, MPI global `rank`, IOR's abstract backend table, debug warnings, and utilities. `S3_statfs` uses `S3_list_service`; `ior.c` relies on `get_file_size`, `stat`, `access`, mkdir/rmdir, and remove hooks for validation and cleanup. The backend is mdtest-enabled.

## Risks And Edge Cases
Global `s3status`/`s3error` are shared mutable state and can carry stale results if callbacks are not invoked as expected. The shared-bucket finalizer deletes the bucket on rank 0 regardless of whether objects remain, which can fail or surprise users. `S3_Xfer` always returns `length` even when libs3 reports an error in compatible mode. File size is incomplete for fragmented files because `S3_stat` has a TODO to sum fragment sizes. Object/bucket name construction can exceed fixed `FILENAME_MAX` buffers and loses or transforms characters. `S3_init` destructively tokenizes `host`, which may affect reused option defaults. Delete heuristics depend on `S3LIB_DELETE_HEURISTICS` and may miss fragments.

## Test Signals
Important coverage includes shared-bucket and bucket-per-file modes, multi-host rank selection, fragmented writes where transfer-size is smaller than block-size, delete with and without `S3LIB_DELETE_HEURISTICS`, stat/get_file_size after fragmented writes, and mdtest mkdir/rmdir/stat behavior against an S3-compatible endpoint.
