# sources/user-network-fs/rclone/backend/fichier/fichier.go

Purpose: This is the main 1Fichier rclone backend. It registers configuration, builds the REST client and directory cache, exposes filesystem features, and implements list, object lookup, upload, mkdir/rmdir, server-side move/copy, quota, and public-link operations.

Important APIs and types: `Options` stores API key, shared folder ID, file/folder passwords, CDN flag, and encoding. `Fs` stores root/name, feature set, options, `dirCache`, HTTP client, pacer, and REST client. Key methods include `FindLeaf`, `CreateDir`, `Name`, `Root`, `String`, `Precision`, `Hashes`, `Features`, `NewFs`, `List`, `NewObject`, `Put`, `putUnchecked`, `PutUnchecked`, `Mkdir`, `Rmdir`, `Move`, `DirMove`, `Copy`, `About`, and `PublicLink`.

Control flow: `NewFs` parses options, makes shared-folder remotes rootless, trims root, creates an authenticated REST client with bearer API key, initializes `dirCache`, then resolves the root. If root lookup fails it probes the parent and object to implement `fs.ErrorIsFile`. `List` delegates to shared folder listing when configured, otherwise calls `listDir`. `Put` checks for an existing object and updates it or calls `PutUnchecked`; `putUnchecked` rejects >300 GB and zero-byte uploads, gets an upload node, ensures the parent path, uploads, finalizes, parses size, and returns an object from the returned link. Move, DirMove, and Copy combine `dirCache` lookups with API helper calls and refresh metadata after successful server-side operations.

State and persistence behavior: Local runtime state is mostly `dirCache` and pacer timing. Server-side state changes include folders, duplicate file uploads, old-version deletion on update, move/copy/rename operations, and file removals. Quota is read from account info. PublicLink returns the object's 1Fichier URL rather than creating a separate sharing artifact.

Dependencies and integration points: It implements `fs.Fs`, `fs.Mover`, `fs.DirMover`, `fs.Copier`, `fs.PublicLinker`, `fs.PutUncheckeder`, and `dircache.DirCacher`. It depends on `fshttp`, `rest`, `pacer`, `encoder`, `hash.Whirlpool`, and helpers in `api.go` and `object.go`.

Risks: Empty files cannot be uploaded. Unknown-size updates are rejected at object level. Server-side move/copy error handling trusts response shapes and first returned URL. `DirMove` depends on `dirCache.DirMove` and the provider's inability to atomically rename and move without overwrite risk. Root-as-file detection mutates `f` after features have already been filled, requiring a workaround noted in comments.

Test signals: The integration test runs the generic rclone suite against `TestFichier:`. The backend advertises Whirlpool hashing, duplicate files, empty directories, and MIME reads, so those generic tests are the main behavioral signals.
