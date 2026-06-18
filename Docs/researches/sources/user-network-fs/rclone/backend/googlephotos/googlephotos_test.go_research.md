# sources/user-network-fs/rclone/backend/googlephotos/googlephotos_test.go

## Purpose
This integration-oriented test file exercises Google Photos behavior that the generic rclone test suite cannot model well because the backend is a virtual, API-limited filesystem.

## Important APIs, Types, And Control Flow
`TestIntegration` creates a Google Photos remote and a local `testfiles` remote. It creates a random app album, uploads a JPEG, checks object methods, optional size probing, unsupported modtime/hash behavior, download content type, album listing, date hierarchy visibility, `NewObject` with and without embedded IDs, file-root detection, and album item removal. It then tests synthetic `upload/` directories with `Mkdir`, `List`, and `Rmdir`, and uploads another file into the upload tree. Final subtests check `Name`, `Root`, `String`, `Features`, `Precision`, and `Hashes`. Helper tests cover `addID`, `addFileID`, and `findID`.

## State And Persistence
The test creates real Google Photos albums/media when credentials are configured. Uploaded synthetic directory state lives only in the backend instance. Album removal is expected to fail because API album deletion is unsupported; uploaded media removal from an album is tested.

## Dependencies And Integration Points
It uses rclone `fs`, local backend import, `fstest`, random name generation, testify, and package internals. It requires test image files and a configured `TestGooglePhotos:` remote unless skipped for missing config.

## Risks And Test Signals
The tests give strong end-to-end signals for Google Photos API compatibility, virtual paths, uploads, ID disambiguation, and downloads. They are slower and credential-dependent, and they do not test all error branches such as read-only mode, batch partial failures, or gphotosdl proxy behavior.
