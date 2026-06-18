# sources/user-network-fs/s3fs-fuse/src/mpu_util.cpp

## Purpose
Implements s3fs utility-mode handling for incomplete multipart uploads. It can list outstanding multipart uploads or abort uploads older than a caller-provided age threshold.

## Important APIs, Types, And Functions
The file defines global `utility_incomp_type utility_mode`, initialized to `NO_UTILITY_MODE`. Private `print_incomp_mpu_list()` formats an `incomp_mpu_list_t` to stdout. Private `abort_incomp_mpu_list(list, abort_time)` filters by upload age and calls `abort_multipart_upload_request()` for matching entries. Public `s3fs_utility_processing(abort_time)` performs the list request, XML parsing, and mode-specific output or abort work.

## Control Flow
`s3fs_utility_processing()` rejects calls unless `utility_mode` is set to list or abort. It creates an `S3fsCurl`, calls `MultipartListRequest(body)`, parses the XML response with `xmlReadMemory()`, converts it with `get_incomp_mpu_list()`, then branches on `utility_mode`. Listing prints all parsed entries. Aborting checks each upload date: `abort_time == 0` means abort all, otherwise ISO8601 parsing must succeed and the upload must be older than `now - abort_time`. The function calls `s3fs_destroy_global_ssl()` before returning.

## State And Persistence Behavior
State is mostly external: S3 multipart upload state is read and optionally modified through S3 API requests. Local global `utility_mode` controls behavior. The XML document is managed by a `unique_ptr` with `xmlFreeDoc`. Output goes to stdout and s3fs logs. There is no local persistent state or checkpointing.

## Dependencies And Integration Points
Dependencies include `S3fsCurl::MultipartListRequest`, `get_incomp_mpu_list()` from `s3fs_xml`, `abort_multipart_upload_request()` from thread/curl request helpers, `get_unixtime_from_iso8601()` from `string_util`, libxml2, and global SSL initialization/teardown from the configured auth backend. This code is reached when s3fs is invoked in incomplete-multipart utility modes rather than mounted as a filesystem.

## Risks
`utility_mode` is a mutable global, so command-line parsing must set it exactly once before utility processing. `s3fs_utility_processing()` always destroys global SSL, which is appropriate for one-shot utility mode but would be risky if invoked from a longer-lived initialized context. Failure to parse an upload date skips that entry rather than aborting or failing the whole operation. Abort errors set an overall failure while continuing iteration, which is useful operationally but can leave partial cleanup. User-facing output is produced with `printf`, bypassing structured logging.

## Test Signals
Tests should mock `MultipartListRequest`, XML parsing, and abort calls to cover empty lists, list mode formatting, abort-all, abort-by-age, malformed dates, individual abort failures, XML parse failure, and list request failure. Integration tests can run against a test bucket with staged multipart uploads and verify that only old uploads are aborted when `abort_time` is nonzero.
