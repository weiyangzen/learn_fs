# sources/user-network-fs/rclone/backend/imagekit/client/upload.go

## Purpose
Implements server-side file upload to ImageKit's upload API.

## Important APIs, Types, and Functions
`UploadParam` contains filename, folder, tags, and optional privacy flag. `UploadResult` models upload response fields including file ID, URL, thumbnail, dimensions, size, file path, AI tags, and version info. `ImageKit.Upload` performs the multipart upload.

## Control Flow
`Upload` rejects blank filenames, constructs form fields including `useUniqueFileName=false`, optional tags/folder/privacy, builds a multipart body with `rest.MultipartUpload`, and posts to `/files/upload` under `UploadPrefix`. The JSON response is decoded into `UploadResult`.

## State and Persistence
The method mutates remote ImageKit media-library state by creating or replacing a file depending on ImageKit's `useUniqueFileName=false` semantics. It has no local persistence.

## Dependencies and Integration Points
Uses rclone `lib/rest` multipart upload helpers and the shared authenticated `rest.Client`. Backend `Put`, `Object.Update`, and `uploadFile` call this method.

## Risks and Edge Cases
The upload body always uses `application/octet-stream`; MIME detection is left to ImageKit. No explicit size validation is done here. `useUniqueFileName=false` is critical to rclone overwrite semantics. As with media models, width uses JSON tag `"Width"`.

## Test Signals
No unit tests target upload construction. The integration test exercises uploads against `TestImageKit:` when configured.
