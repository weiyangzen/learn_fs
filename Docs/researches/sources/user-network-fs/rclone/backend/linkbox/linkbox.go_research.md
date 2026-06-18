
# sources/user-network-fs/rclone/backend/linkbox/linkbox.go

## Purpose
Implements rclone support for Linkbox cloud storage using both Linkbox's open API and web API.

## Important APIs, Types, And Control Flow
Core types are `Options`, `Fs`, `Object`, `entity`, response wrappers, and upload response structs. `NewFs` parses token/email/password, builds normal and CDN REST clients, disables HTTP/2 and sets a browser-like user agent for CDN downloads, restores or obtains a web token, and initializes `dircache`. `login` obtains and stores the web token. `listAll`, `FindLeaf`, `CreateDir`, `List`, `NewObject`, `Mkdir`, `Rmdir`, and `Purge` are directory-cache driven. `Open` downloads via stored or refreshed CDN URL. `Update` rejects empty/unknown size, deletes existing files, hashes the first 10 MiB, requests an upload URL or dedupe status, uploads via PUT if needed, finalizes with `folder_upload_file`, and polls for eventual consistency.

## State And Persistence
Persistent config includes open API token, email, obscured password, and cached `web_token`. Runtime state includes pacer, REST clients, directory cache, web token protected by mutex, and object entity data. Remote state is Linkbox folders/files and object deletion/recreation during update.

## Dependencies And Integration Points
Uses rclone `fs`, `rest`, `fshttp`, `pacer`, `fserrors`, `hash`, `obscure`, and `dircache`. Implements `Fs`, `Purger`, `DirCacheFlusher`, and `Object`; public sharing is intentionally omitted because Linkbox links are page links rather than direct file links.

## Risks And Test Signals
Risks include two-token authentication drift, web-token refresh retry semantics, Linkbox status-code quirks, case-insensitive matching, pagination limit, delete-before-upload data loss on later failures, inability to upload empty or unknown-sized files, first-10-MiB hash protocol assumptions, CDN fingerprint workarounds, and eventual consistency polling. Tests should cover token refresh, list pagination, dircache create/find/flush, upload status 1 and 600 paths, empty/unknown upload rejection, remove/rmdir error mapping, and download URL refresh.
