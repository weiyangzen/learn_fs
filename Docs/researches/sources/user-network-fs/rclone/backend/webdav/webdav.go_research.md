# sources/user-network-fs/rclone/backend/webdav/webdav.go

Purpose: main generic WebDAV backend with vendor-specific behavior for Fastmail, Nextcloud, ownCloud, Infinite Scale, SharePoint, SharePoint NTLM, rclone WebDAV, and generic servers.

Important APIs: `Options`, `Fs`, `Object`, `NewFs`, `setQuirks`, `shouldRetry`, auth/header helpers, `listAll`, `List`, `ListP`, `NewObject`, `Put`, `PutStream`, mkdir/rmdir/purge, `Copy`, `Move`, `DirMove`, `About`, and object `Open`, `Update`, `SetModTime`, `Hash`, `Remove`, `readMetaData`.

Control flow/state: initialization normalizes URL/root, reveals password, configures auth, headers, NTLM-safe transport, error handler, vendor quirks, and root-as-file detection. Listing uses PROPFIND, Depth, optional prop bodies, URL joining/decoding, and share/mount filters. Update creates parents, then chooses TUS, Nextcloud chunked upload, or simple PUT. Object metadata is cached after PROPFIND and refreshed after writes.

Dependencies/integration: WebDAV API XML types, SharePoint cookie auth, Azure NTLM, singleflight, rclone config/fs/hash/list/rest/pacer/encoder, and standard HTTP/XML/path packages. Implements purge, putstream, copy, move, dirmove, listp, about, and object interfaces.

Risks/test signals: vendor quirks, auth refresh, redirect credential handling, path escaping, upload cleanup, PROPFIND variance, and weak hash/modtime support. Tests cover integration remotes, headers, auth redirect, reserved character escaping, and API status parsing.
