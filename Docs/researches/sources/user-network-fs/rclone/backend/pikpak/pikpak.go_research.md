# sources/user-network-fs/rclone/backend/pikpak/pikpak.go

Purpose: main PikPak rclone backend. It registers `pikpak`, performs username/password plus captcha-backed authorization, maps Drive files/folders to rclone, and implements listing, upload, copy/move, trash, cleanup, public links, quota/user info, and backend commands.

Important APIs/types/functions: `Options` stores credentials, device/user IDs, user agent, root folder, trash/media-link behavior, hash threshold, chunk/cutoff/concurrency, and encoding. `Fs` stores REST and HTTP clients, dircache, pacer, config mapper, and token mutex. `Object` stores metadata, parent, GCID, MD5, and cached link. Core functions include `pikpakAuthorize`, `newFs`, `NewFs`, `shouldRetry`, `newClientWithPacer`, `listAll`, `List`, `CreateDir`, `Mkdir`, `About`, `PublicLink`, `deleteObjects`, `purgeCheck`, `CleanUp`, `Move`, `Copy`, `uploadByResumable`, `upload`, `Put`, `UserInfo`, `Command`, and object `Open`/`Update`/`upload`.

Control flow: config ensures a token exists or runs signin. Initialization validates upload settings, ensures a device ID, creates OAuth/captcha clients, derives user ID from the access token, initializes dircache, and detects file roots. Listing builds JSON filters and pages `/drive/v1/files`. Upload tries server-side GCID lookup via CID, computes GCID if needed, requests an upload ticket, returns immediately for instant completed uploads, otherwise uses S3 singlepart or multipart upload and waits for any task. Updating uploads a temp object, deletes the old object, then renames the temp object. Copy/move compensate for PikPak collision behavior and attempt rollback.

State and persistence: config persists device ID, OAuth token, and captcha token. Remote state includes files, folders, trash, shares, tasks, quotas, and upload sessions. Local state includes dircache, cached links/metadata, pacer, and token mutex. GCID hashing may buffer data in memory or disk.

Dependencies/integration: integrates rclone `fs`, `oauthutil`, `dircache`, `encoder`, `pacer`, `rest`, `random`, AWS S3 SDK, PikPak API types, helpers, and multipart upload code.

Risks/test signals: modtimes cannot be set, so precision is `ModTimeNotSupported`. Multithreaded downloads are disabled. Copy/move collision rollback may not fully restore auto-renamed files. Updating deletes the old object before final rename. Runtime auth refresh mutates config. Integration tests and compile-time interface assertions cover major rclone surfaces; `ListR`, `ChangeNotifier`, and `PutStreamer` are intentionally not asserted.
