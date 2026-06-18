# sources/user-network-fs/rclone/backend/webdav/chunking.go

Purpose: Nextcloud chunked upload support using WebDAV upload directories.

Important APIs: `shouldRetryChunkMerge`, `setUploadChunkSize`, `getChunksUploadDir`, `getChunksUploadURL`, `shouldUseChunkedUpload`, `updateChunked`, `uploadChunks`, `createChunksUploadDirectory`, `mergeChunks`, `purgeUploadedChunks`.

Control flow/state: creates/purges a stable upload dir, uploads sequential byte-range chunk objects with repeatable readers, then MOVEs `.file` to the final destination. Merge retry handles 423 Locked with exponential sleeps and treats a later 404 as success after a lock was seen.

Dependencies/integration: rclone `fs`, `readers`, `rest`, and standard crypto/http/path/time. Selected from `Object.Update` for Nextcloud when file size exceeds configured chunk size.

Risks/test signals: endpoint must match `/dav/files/USER`; chunking is sequential; failed merges rely on future purge cleanup. Nextcloud integration tests cover chunked upload.
