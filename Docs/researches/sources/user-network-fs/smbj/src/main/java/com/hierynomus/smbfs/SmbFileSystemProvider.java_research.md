# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileSystemProvider.java

Purpose: `SmbFileSystemProvider` is the NIO service provider for `smb://` URIs. It creates and caches one `SmbFileSystem` per identity, host, and share.

Important APIs and control flow: `newFileSystem` builds a cache key, rejects duplicates, resolves auth from URI user-info and environment properties, selects port 445 by default, and delegates creation to a `Factory`. `getPath` strips the share prefix from the URI path and returns root or a share-relative path. NIO operations mostly validate `SmbPath` and forward to `SmbFileSystem`.

State, dependencies, and integration: `fileSystems` is guarded with synchronization. `FactoryImpl` wires `SMBClient`, `ShareSourceImpl`, host, port, `AuthenticationContext`, and share name. Passwords may come from URI, `String`, or `char[]`.

Risks: cache key omits password, so two credentials with the same identity collide. `removeFileSystem` removes from a map during enhanced iteration, relying on immediate return. Cross-filesystem move copies then deletes, but does not preserve all copy semantics. Many NIO features are unimplemented. Tests should cover URI parsing, env override precedence, duplicate detection, provider mismatch, cross-filesystem fallback, and invalid share URIs.
