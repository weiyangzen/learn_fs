# sources/test-tools/ior/src/aiori-S3-4c.c

## Purpose
Implements the legacy aws4c/libcurl S3 backend family for IOR: `S3-4c` for standard multipart-upload S3 semantics, `S3_plus` for S3 plus EMC extensions, and `S3_EMC` for EMC byte-range writes. It adapts IOR's abstract I/O table to object-store operations, including bucket setup, object create/open, ranged reads, multipart write assembly, pseudo-delete, and object size lookup.

## Important APIs, Types, And Functions
Defines `s3_options_t` with bucket/user/host options plus runtime `IOBuf` state, ETag accumulation, multipart `UploadId`, part numbering, curl flags, and written-state tracking. Registers `s3_4c_aiori`, `s3_plus_aiori`, and `s3_emc_aiori`. Key functions are `S3_options`, `S3_init`, `S3_finalize`, `S3_check_params`, `s3_connect`, `S3_Create_Or_Open_internal`, `S3_Xfer_internal`, `S3_Close_internal`, `S3_Delete`, `EMC_Delete`, and `S3_GetFileSize`.

## Control Flow
Initialization calls `aws_init`; first open/create lazily runs `s3_connect`, reads aws4c credentials, creates/reuses the bucket on rank 0, initializes `IOBuf` structures, and enables EMC extensions if requested. Create/open returns the object name cast as an `aiori_fd_t *`; for multipart writes, rank 0 initiates MPU for N:1 and broadcasts the `UploadId`. Transfers either upload parts and store ETags, perform EMC byte-range PUTs/appends, or issue ranged GETs expecting HTTP 206. Close finalizes MPU by gathering ETags to rank 0 for N:1, formatting `CompleteMultipartUpload` XML in correct segmented/strided order, posting completion, resetting MPU buffers, and synchronizing ranks. Deletes overwrite with a zero-length object because of documented EMC append/delete/recreate behavior.

## State And Persistence Behavior
The backend stores per-rank runtime state in `s3_options_t`, but it is explicitly not safe for concurrent access to multiple files. It persists benchmark data as S3 objects under a configured bucket and uses zero-length replacement instead of actual deletion. Multipart state is held in `UploadId`, `part_number`, and an accumulated ETag `IOBuf` until close. Rank synchronization via `testComm` controls bucket creation, UploadId sharing, MPU completion, and read-after-write visibility.

## Dependencies And Integration Points
Depends on aws4c/`aws4c_extra`, libcurl, libxml2, MPI globals `rank` and `testComm`, `aiori.h`, `ior.h`, and debug/error macros. IOR supplies transfer hints through `S3_xfer_hints`; `ior.c` invokes this backend through the `ior_aiori_t` hooks for create/open/xfer/close/remove/get_file_size/fsync.

## Risks And Edge Cases
`S3_Xfer` calls `S3_Xfer_internal` but does not return its value, which violates the `xfer` contract and can corrupt IOR's byte-count checks. The code depends on global `hints`; create/open dereferences it for N:1/N:N decisions. Standard S3 cannot append, and `S3_check_params` only rejects one N:1 strided case. Multipart part numbering starts at `0` in generated XML although S3 APIs commonly expect one-based part numbers. ETag gathering for large N:1 jobs can exhaust rank 0 memory and is constrained by S3 MPU part limits noted in comments. `UploadId` length check uses `>` instead of `>=` against the fixed buffer size. Pseudo-delete leaves buckets and zero-length objects behind.

## Test Signals
Useful signals include S3/EMC IOR write/read/check runs in file-per-process and shared-file modes, transfer-size equal and smaller than block-size, verbose MPU ETag output, HTTP status validation, final aggregate file-size checks in `ior.c`, and data verification failures from `WRITECHECK`/`READCHECK`. A focused unit or integration test should catch the missing return from `S3_Xfer`.
