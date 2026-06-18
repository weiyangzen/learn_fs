# sources/user-network-fs/rclone/backend/pixeldrain/pixeldrain.go

Purpose: main PixelDrain Filesystem rclone backend. It registers `pixeldrain`, configures API key and root folder, exposes metadata support, and maps PixelDrain nodes into rclone directories, objects, changes, public links, quota, and server-side moves.

Important APIs/types/functions: `Options` stores API key, root folder ID, and API URL. `Fs` stores root, REST client, pacer, auth flag, and normalized `pathPrefix`. `Object` wraps a `FilesystemNode`. `NewFs` parses config, sets features, configures REST root and auth, verifies login for `me`, builds path prefix, and handles file-root detection. Methods include `List`, `NewObject`, `Put`, `Mkdir`, `Rmdir`, `Purge`, `Move`, `DirMove`, `ChangeNotify`, `PutStream`, `DirSetModTime`, `PublicLink`, `About`, and object methods for metadata/hash/open/update/remove.

Control flow: all API paths add `pathPrefix` and returned paths strip it. Listing stats the directory then converts children. Upload collects metadata, defaults missing `mtime` from source modtime, and calls `put`. Move/DirMove call shared `rename` and translate wrapper errors to rclone errors. ChangeNotify enables logging for non-`/me/` roots and polls change logs at the supplied interval.

State and persistence: persistent remote state includes filesystem nodes, metadata, share IDs, and change logging. Local state is options, path prefix, client, pacer, and object node snapshots. Public links toggle remote `shared` metadata and construct a download URL from API URL and returned ID.

Dependencies/integration: uses rclone `fs`, `configstruct`, `fshttp`, `hash`, `pacer`, and `rest`; delegates HTTP details to `api_client.go`. Supports SHA256 and metadata keys `mode`, `mtime`, `btime`.

Risks/test signals: unauthenticated `me` access is rejected. ChangeNotify immediately reads the first interval from the channel. `Object.Update` mutates the local node before remote upload completes. Public link URL rewriting assumes standard `/api` URL shape. Integration tests skip invalid UTF-8 because PixelDrain rejects it.
