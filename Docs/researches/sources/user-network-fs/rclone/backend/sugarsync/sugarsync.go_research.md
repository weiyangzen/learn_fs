# sources/user-network-fs/rclone/backend/sugarsync/sugarsync.go

## Purpose

`sugarsync.go` implements the rclone backend for SugarSync's XML API. It handles interactive refresh-token setup, authorization renewal, directory caching, file and folder operations, copy/move, soft/hard delete, and public links.

## Important APIs, Types, and Functions

`Options` stores app credentials, delete mode, refresh/authorization tokens, cached user/root/deleted IDs, and encoding. `Fs` owns REST client, pacer, config mapper, auth mutex/expiry, and `dircache`. `Object` stores metadata, ID, size, and modtime. Key functions include `withDefault`, registration `Config`, `getAuthToken`, `getAuth`, `getUser`, `NewFs`, `errorHandler`, `FindLeaf`, `CreateDir`, `listAll`, `List`, `Put`, `PutUnchecked`, `delete`, `purgeCheck`, `Copy`, `Purge`, `moveFile`, `moveDir`, `Move`, `DirMove`, `PublicLink`, object metadata/read/update/remove, and `ID`.

## Control Flow

Config prompts for username/password only to obtain a refresh token. Runtime auth uses a REST signer: before each request, `getAuth` refreshes authorization if missing or near expiry, caches auth URL/expiry/user back into config, and sets the `Authorization` header. `NewFs` discovers and caches root/deleted IDs from `/user`, initializes dircache, and handles root-as-file. Listing pages through `/contents` with `max=500`. Upload creates an empty file resource if needed, then PUTs `/data`; if a newly created upload fails, it deletes or moves the partial file according to delete mode. Soft delete moves resources to the deleted folder; hard delete issues DELETE.

## State and Persistence Behavior

Persistent config can be updated with refresh token, authorization URL, authorization expiry, user URL, root ID, and deleted ID. Runtime state includes auth mutex, auth expiry, directory cache, object metadata, and pacer. Remote state includes files, folders, sync folders, deleted folder entries, public-link flags, and file data.

## Dependencies and Integration Points

It depends on SugarSync XML DTOs, rclone config/fs/http/rest/pacer/dircache/operations helpers, obscure credentials, and encoder. It implements purge, streaming upload, copy, move, dir move, dir-cache flush, public link, and ID interfaces.

## Risks and Edge Cases

The API returns HTML error bodies, parsed by regex for `<h3>`. Modtime setting is unsupported. Root sync-folder creation needs a non-canonical `*X-SugarSync-API-Version` header and may not return a location, requiring lookup. Hard-delete purge is disabled because deleting folders can orphan contents. Case-insensitive paths can make same-name copy unsafe. Auth refresh writes config during operations.

## Test Signals

Integration uses `TestSugarSync:Test` because root sync-folder moves can fail. Unit tests cover HTML error parsing. Strong signals include token renewal, paginated listing, upload cleanup, soft versus hard delete, copy overwrite cleanup, public links, and dircache correctness after moves/deletes.
