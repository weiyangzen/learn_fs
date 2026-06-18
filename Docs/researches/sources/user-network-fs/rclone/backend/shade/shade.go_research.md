# sources/user-network-fs/rclone/backend/shade/shade.go

Purpose: implements the rclone backend for Shade FS, including token acquisition, file/directory operations, reads via direct or presigned URLs, server-side move, and integration with multipart upload support.

Important APIs/types/functions: constants define Shade endpoints, pacer timing, and upload limits. `Options` stores drive ID, API key, endpoint, chunk settings, concurrency, and cached token values. `Fs` holds REST clients, drive/root, pacer, token cache/mutex, config mapper, and created-directory cache. `Object` and `Directory` implement rclone object/directory surfaces. Key functions include `refreshJWTToken`, `callAPI`, `NewFS`, `Move`, `DirMove`, `NewObject`, `Put`, `List`, `ensureParentDirectories`, `ensureDirectoryPath`, `Mkdir`, `Rmdir`, `buildFullPath`, `Object.Open`, `Object.Update`, and `Object.Remove`.

Control flow: initialization parses options, creates clients, sets features, validates chunk size, restores token expiry if present, refreshes a JWT, and detects file-root remotes. `refreshJWTToken` returns a still-valid token or fetches a new one from the Shade API, decodes JWT expiry, and persists token fields to config. `callAPI` wraps authenticated Shade FS requests through the pacer. Listing filters draft entries and makes API paths relative to the configured root. Reads first call `/fs/download`; HTTP 200 returns the body directly, while 307 body is treated as a presigned URL and fetched with range options. Directory creation walks parents and treats conflict/unprocessable as existing.

State and persistence behavior: JWT token and expiry are persisted in the config mapper; `createdDirs` is an in-memory cache guarded by RW mutex. No content hashes or modtimes are set through the API.

Dependencies/integration: integrates rclone `fs`, `rest`, `fshttp`, `pacer`, `encoder`, `object.NewStaticObjectInfo`, and Shade API DTOs. Advertises empty directories, move, dir move, and chunk writer.

Risks/test signals: risks include token expiry parsing, status handling when responses are nil, directory-cache staleness, query escaping/unescaping, unsupported hashes/modtime, and presigned URL range behavior. `shade_test.go` supplies live integration coverage only.
