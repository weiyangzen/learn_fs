# sources/object-store/minio-mc/cmd/subnet-file-uploader.go

## Purpose
Provides a multipart uploader for sending local diagnostic/profile/support files to MinIO SUBNET, with optional zstd compression, stream encryption, custom public keys, response credential extraction, and post-upload deletion.

## Important APIs, types, and functions
- `SubnetFileUploader` carries alias, file path/name, request URL, query params, headers, compression/encryption/delete flags, and optional public key.
- `UploadFileToSubnet` builds the upload request, sends it, optionally deletes the local file, and saves credentials returned by SUBNET.
- `updateParams` derives filename, appends `.zst` and/or `.enc`, records query params, and appends them to `ReqURL`.
- `subnetUploadReq` creates a streaming multipart POST request using `io.Pipe`.
- `bytesToPublicKey` decodes PEM if present and parses an RSA PKCS#1 public key.

## Control flow
Upload begins by calling `subnetUploadReq`, which updates URL params and starts a goroutine to stream the file into a multipart form. The goroutine opens the file, creates a form file part, optionally wraps it in an encrypted stream using `madmin/estream` and either the supplied public key or a default key, optionally wraps it in a zstd writer, then copies file bytes. The request is posted via `subnetReqDo`. On success it deletes the source file if requested and extracts/saves SUBNET credentials when an alias is configured.

## State and persistence
Reads local files, can delete the uploaded local file, mutates `SubnetFileUploader` fields (`filename`, `Params`, `ReqURL`, `AutoCompress`), and can persist API key/license config through `extractAndSaveSubnetCreds`.

## Dependencies and integration points
Uses SUBNET HTTP helper `subnetReqDo`, `SubnetHeaders`, `extractAndSaveSubnetCreds`, zstd compression, MinIO `estream` encryption, default public key from elsewhere in the package, and standard multipart streaming.

## Risks and edge cases
- `updateParams` appends query params to `ReqURL` each call; reusing the same uploader can duplicate params.
- `UploadFileToSubnet` ignores errors from `os.Remove` and from `extractAndSaveSubnetCreds`.
- Compression writer creation ignores its error (`z, _ := zstd.NewWriter`).
- Streaming errors are propagated through `CloseWithError`, but request creation succeeds before the file is opened.
- `bytesToPublicKey` only parses PKCS#1 RSA public keys, not PKIX public key blocks.

## Test signals
No direct tests in this subset. Tests should cover URL parameter mutation, compression/encryption filename suffixes, PEM/key parsing, streaming error propagation, delete-after-upload behavior, and credential-save error handling.
