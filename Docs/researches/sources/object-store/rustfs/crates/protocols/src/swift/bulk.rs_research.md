# sources/object-store/rustfs/crates/protocols/src/swift/bulk.rs

## Purpose
This file implements Swift bulk operations: bulk delete and bulk archive extract. Bulk delete processes a newline-separated list of `/container/object` paths and deletes each object through the Swift object layer. Bulk extract accepts a tar, tar.gz, or tar.bz2 archive, extracts regular file entries into memory, and uploads them into one container.

## Important APIs, Types, And Functions
- `DeleteResult` and `ExtractResult` model per-item outcomes, although only aggregate response structures are serialized by handlers.
- `BulkDeleteResponse` serializes Swift-style fields such as `Number Deleted`, `Number Not Found`, `Errors`, `Response Status`, and `Response Body`.
- `BulkExtractResponse` serializes `Number Files Created`, `Errors`, and response status/body fields.
- `parse_object_path(path)` trims a path, strips leading slashes, and splits it into container and object key.
- `handle_bulk_delete(account, body, credentials)` loops over request-body paths, calls `object::delete_object`, counts deleted/not-found/errors, and returns a JSON `200 OK` response.
- `ArchiveFormat::{Tar, TarGz, TarBz2}` and `ArchiveFormat::from_query` parse Swift `extract-archive` formats including aliases `tgz`, `tbz2`, and `tbz`.
- `handle_bulk_extract(account, container, format, body, credentials)` checks that the container exists, extracts archive entries, uploads each entry with `object::put_object`, and returns a JSON response.
- `extract_tar_entries(format, body)` builds an async tar reader, optionally wraps gzip/bzip2 decoders, skips directories, and returns `(path, bytes)` pairs for files.

## Control Flow
Bulk delete starts with structured debug logging, filters blank body lines, and rejects empty requests. Each path is parsed independently. A successful delete increments `number_deleted`; `SwiftError::NotFound` increments `number_not_found`; any other delete error is appended to `Errors` and represented as a per-item 500. Invalid path syntax is appended as a 400-style error. The overall Swift response body marks `"400 Bad Request"` if any errors occurred, but the HTTP status returned by the axum response is always `200 OK`, matching common Swift bulk response patterns where per-item status is in the JSON body.

Bulk extract validates the target container by calling `container::get_container_metadata`. It fully buffers the archive request body and then `extract_tar_entries` fully buffers every file entry before upload begins. It then uploads entries sequentially with an empty header map. Created files increment `number_files_created`; upload failures are collected in `Errors`. If zero files are created, response status and HTTP status become bad request; otherwise HTTP status is `201 Created`, even with per-file errors.

Archive extraction chooses a reader based on `ArchiveFormat`, iterates tar entries asynchronously, converts each tar path with `to_string_lossy`, skips directories, and reads regular entry contents to a `Vec<u8>`. Read failures for individual entries are logged and skipped rather than aborting the entire extraction.

## State And Persistence Behavior
Bulk delete mutates object storage by calling the Swift object delete path for each requested object. Bulk extract mutates object storage by creating or overwriting objects in the target container through `object::put_object`. This file does not directly access S3 buckets; all object persistence goes through the Swift `container` and `object` modules.

Response state is accumulated in local structs and serialized to JSON. No durable operation log or transaction state is maintained. Bulk operations are partial-success workflows: earlier successful deletes/uploads are not rolled back if later items fail.

## Dependencies And Integration Points
The module depends on `object::delete_object`, `object::put_object`, `container::get_container_metadata`, Swift error/result types, axum response builders, `s3s::Body`, serde JSON serialization, `futures::StreamExt`, `tokio_tar`, `async_compression`, Tokio async I/O, and transaction id generation from `super::handler`.

It is an HTTP handler support module for Swift routes such as `DELETE /?bulk-delete` and `PUT /{container}?extract-archive=<format>`.

## Risks And Edge Cases
- Bulk extract buffers the entire archive and all file contents in memory. Large archives can cause high memory usage; there are no local entry count, total size, or per-file limits.
- Tar entry paths are accepted as lossy strings and passed directly to `put_object`. This file does not reject absolute paths, `..`, duplicate entries, special file types other than directories, or path names that may be surprising as object keys.
- Entry read failures are logged and skipped without adding an error to the response, which can make archives appear more successful than they were.
- Bulk delete keeps processing after errors and returns HTTP 200 even when JSON `Response Status` is `"400 Bad Request"`; clients must inspect the body.
- `DeleteResult` and `ExtractResult` are accumulated partly or defined but not serialized in the final response, so detailed status is limited to `Errors`.
- Uploads in bulk extract use an empty header map, so content type and metadata from archive entries are not preserved.

## Test Signals
Unit tests cover object-path parsing, invalid paths, archive format parsing and aliases, default response values, body line filtering, and, behind the `swift` feature, tar extraction for plain tar, gzip, bzip2, directory skipping, invalid tar errors, and empty archives. There are no storage-backed handler tests for partial delete/upload behavior, response status/body coupling, or transaction id headers.
