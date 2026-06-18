# sources/user-network-fs/rclone/backend/premiumizeme/premiumizeme.go

## Purpose
Implements rclone's `premiumizeme` backend for premiumize.me cloud storage. It registers OAuth/API-key configuration, maps rclone filesystem operations onto premiumize.me folder/item REST endpoints, and exposes object metadata, upload, delete, move, quota, public-link, directory-cache, and shutdown behavior.

## Important APIs, Types, And Functions
The main exported types are `Options`, `Fs`, and `Object`. `init` registers the backend with OAuth shared options plus hidden `api_key` and encoding controls. `NewFs` builds the REST client, OAuth token renewer, pacer, features, and `dircache.DirCache`; it also handles roots that point at files by returning `fs.ErrorIsFile`. Core helpers include `parsePath`, `shouldRetry`, `errorHandler`, `baseParams`, `readMetaDataForPath`, `listAll`, `createObject`, `renameLeaf`, and `remove`. `Fs` implements listing, mkdir/rmdir/purge, put/update, move/dirmove, public links, quota, hashes, and cache flush. `Object` implements rclone object metadata, open, update, remove, mime type, and ID.

## Control Flow
Construction chooses OAuth unless `api_key` is set, then wraps all API calls in `f.pacer.Call` with retry handling for network errors plus HTTP 429, 500, 502, 503, 504, and 509. Directory lookup flows through `dircache`: `FindLeaf` searches `/folder/list`, `CreateDir` posts `/folder/create`, and `List` turns API content into `fs.Dir` or `Object`. Upload flow requests `/folder/uploadinfo`, validates that the returned upload host resolves, optionally renames an existing file aside, uploads multipart form data to the returned URL, removes the old file after success, and rereads metadata. Move flow separates rename and parent-directory move because premiumize.me has different endpoints for those operations.

## State And Persistence
Persistent service state is remote folders, files, item IDs, server-created upload URLs/tokens, shareable download links, and quota. Local state is limited to the in-memory dir cache, object metadata cache fields, the OAuth token source/renewer, and pacer timing. The backend does not write repository files; rclone config stores OAuth credentials or an API key outside this source file.

## Dependencies And Integration Points
This file integrates with rclone's `fs`, `config`, `oauthutil`, `rest`, `pacer`, `dircache`, `encoder`, `hash`, and `fshttp` packages plus local `premiumizeme/api` response types. It uses the premiumize.me API under `https://www.premiumize.me/api`, OAuth endpoints under premiumize.me, and rclone feature interfaces `Purger`, `Mover`, `DirMover`, `Abouter`, `PublicLinker`, `Shutdowner`, `MimeTyper`, and `IDer`.

## Risks And Test Signals
Risks include `Shutdown` calling `f.tokenRenewer.Shutdown()` even when API-key mode leaves `tokenRenewer` nil, upload replacement temporarily renaming the old file and depending on rollback if the upload fails, case-insensitive name matching causing ambiguous matches, `PublicLink` returning the existing download URL rather than creating an explicit permission, and metadata using creation time because modtime is unsupported. Test signals should cover OAuth and API-key auth, root-as-file setup, empty directories, upload replacement rollback, move plus rename across folders, purge safety on root, public-link behavior, retryable status handling, and nil-renewer shutdown.
