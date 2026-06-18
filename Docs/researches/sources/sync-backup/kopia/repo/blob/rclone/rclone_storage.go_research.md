# sources/sync-backup/kopia/repo/blob/rclone/rclone_storage.go

Purpose: implements a storage provider by launching `rclone serve webdav` locally and delegating blob operations to Kopia's WebDAV storage.

Important APIs/types/functions: `rcloneStorage`, `ListBlobs`, `GetMetadata`, `GetBlob`, `ConnectionInfo`, `Kill`, `Close`, `DisplayName`, `processStderrStatus`, `remoteControl`, `forgetVFS`, `rcloneURLs`, `runRCloneAndWaitForServerAddress`, `New`, and provider `init`.

Control flow: `New` creates a temp dir, generates TLS cert/key and htpasswd credentials, optionally writes embedded rclone config, builds rclone arguments with mandatory local random WebDAV and RC addresses, starts rclone without inheriting cancellation, scans stderr until both WebDAV and remote-control URLs are detected, configures an HTTP client trusting the generated cert, builds an underlying WebDAV storage, and stores it. Read/list/metadata operations first call RC `vfs/forget` to flush rclone caches, then delegate. `Close` closes WebDAV storage, kills rclone, waits, and removes temp dir. `remoteControl` POSTs JSON with basic auth to the RC endpoint.

State and persistence behavior: temporary TLS/config/auth files live under a temp directory and are removed on close or failed construction. Blob persistence is in the rclone remote backend. A live child process is provider state.

Dependencies/integration points: depends on external `rclone`, WebDAV provider, TLS utilities, htpasswd, uuid, process management, and remote-control API. Risks include startup-log regex fragility, process cleanup on crashes, external binary/version differences, credentials in embedded config/temp files, cache invalidation overhead, and provider data-loss warning. Tests cover startup cancellation, storage behavior, shard behavior, invalid exe/flags, provider matrix, and cleanup.
