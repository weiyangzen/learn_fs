# sources/user-network-fs/rclone/backend/ulozto/ulozto.go

Purpose: rclone backend implementation for Uloz.to. It registers config, authenticates, resolves a root folder, uses `dircache`, maps rclone file/directory operations to Uloz.to APIs, uploads via private sessions/CDN URLs, and stores rclone metadata in file descriptions.

Important APIs/types/functions: `Options`, `Fs`, `UploadSession`, `DescriptionEncodedMetadata`, `Object`, and `RenamingObjectInfoProxy`. Key methods include `NewFs`, `authenticate`, `shouldRetry`, `About`, `Put`, `PutUnchecked`, `uploadUnchecked`, `Mkdir`, `Rmdir`, `Move`, `DirMove`, `List`, `NewObject`, `FindLeaf`, `CreateDir`, object `Open`, `Update`, `Remove`, `SetModTime`, and `Hash`.

Control flow/state: `NewFs` strips root slashes, creates REST/CDN clients, sets app/user tokens, authenticates, and initializes `dircache`. Upload flow creates an upload session, tees payload into MD5/SHA256 hashers, posts multipart payload to the CDN URL, verifies returned MD5, encodes mtime/hashes in description, patches file properties to final folder/name, and confirms the batch. Listing pages until a short page is returned. Object update uploads a replacement first, deletes the old file twice, then copies new metadata into the wrapper.

Dependencies/integration: rclone `fs`, config, `fshttp`, `hash`, `dircache`, `encoder`, `pacer`, `rest`, `obscure`, and Uloz.to API types. Implements duplicate files, empty directories, put-unchecked, mover, dir mover, and dir-cache flush interfaces.

Risks/test signals: multi-step upload replacement can leave partial remote state if later delete/commit fails; metadata is only as trustworthy as the description field; duplicate names require careful first-match logic; reauth is tied to 401 error code `70001`. Tests cover generic integration and missing-description metadata behavior.
