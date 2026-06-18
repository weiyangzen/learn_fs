# sources/user-network-fs/rclone/backend/box/box.go

## Purpose
Main rclone backend implementation for Box. It registers `box`, supports OAuth2/access-token/JWT app auth, maps paths to Box IDs through a directory cache, implements listing, metadata, upload/update dispatch, directory operations, server-side copy/move, public links, trash cleanup, quota, change notifications, and feature declarations.

## Important APIs, types, and functions
Auth helpers load Box app config, decrypt PKCS8 private keys, build JWT claims, and refresh tokens. `Options` stores upload cutoff, commit retries, encoding, root folder ID, access token, list chunk size, owner filter, and impersonation. `Fs` stores REST client, dir cache, pacer, token renewer, upload tokens, and item metadata cache. `Object` stores path, metadata flag, size, modtime, ID, public link, and SHA1.

`NewFs` chooses auth mode, sets headers, initializes token renewal and dir cache, detects file roots, and fills features. `readMetaDataForPath`, `preUploadCheck`, `listAll`, and `ListP` are core lookup/listing paths. `Put`, `PutUnchecked`, `Object.Update`, and `Object.upload` handle create/update and simple upload; large multipart is delegated to `upload.go`. `Copy`, `Move`, `DirMove`, `PublicLink`, `CleanUp`, `ChangeNotify`, and `changeNotifyRunner` implement higher-level Box behavior.

## Control flow
Startup authenticates and resolves the configured root folder ID/path. Listing pages `/folders/{id}/items`, filters by type/status/owner, decodes names, caches subfolder IDs, creates objects, and records item metadata for event handling. `Put` uses Box pre-upload checks to choose create vs update. Copy handles case-insensitive conflicts by copying to a temp name, deleting the destination, then moving. Change notification polls `/events`, filters duplicates and unsupported types, uses sequence IDs and cached parent/name data to notify old and new paths.

## State and persistence
Remote state is Box files, folders, versions, shared links, trash, and upload sessions. Local runtime state includes directory cache, item metadata cache, token renewer, upload tokens, REST/pacer state, and object metadata. `root_folder_id` changes the remote root.

## Dependencies and integration points
Uses rclone `fs`, `dircache`, `oauthutil`, `jwtutil`, `encoder`, `rest`, `pacer`, `fshttp`, and Box API types. Integrates with Box API and upload endpoints, rclone VFS/change-notification consumers, generic fstests, and `upload.go`.

## Risks
Box case-insensitivity and filename constraints complicate copy/move. `getDecryptedPrivateKey` type-asserts RSA keys and can panic on unexpected parsed key types. `Shutdown` unconditionally calls `tokenRenewer.Shutdown`, risking nil dereference when no renewer exists. Change notification path reconstruction is best-effort and depends on cached parents. `Size`/`ModTime` hide metadata errors with default values. Box-specific auth, events, and cleanup have no direct tests in the listed set.

## Test signals
`box_test.go` runs generic fstests. Interface assertions document expected support for purger, streamer, copier, abouter, mover, dir mover, dir cache flusher, public linker, clean-upper, list-per, shutdowner, object, and IDer.
