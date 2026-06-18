# File Research: sources/os/linux/linux/fs/smb/server/vfs.c

Implements ksmbd’s Linux VFS operation layer, mapping SMB file semantics onto kernel path, file, xattr, ACL, sparse, copy, and metadata APIs.

Key behaviors:
- Performs share-root-relative path lookup with `LOOKUP_BENEATH`, optional cross-mount following, symlink avoidance where requested, and special removal/creation lookup flows.
- Supports caseless lookup by scanning directories and comparing names with Unicode-aware `utf8_strncasecmp` when available, falling back to `strncasecmp`.
- Creates files and directories, optionally inheriting parent owner based on share config.
- Implements read/write for normal files and alternate data streams stored as xattrs.
- Enforces SMB byte-range lock conflicts before read/write/truncate/copy when POSIX extensions are not active.
- Breaks level-II oplocks before writes, truncates, zero-data, and copy-to-destination operations.
- Implements fsync, getattr, unlink/rmdir, hardlink, rename, truncate, directory-empty checks, and delete helper flows with proper mount write acquisition.
- Wraps list/get/set/remove xattr operations, including case-insensitive xattr lookup for streams.
- Maps SMB caching hints to Linux flags/readahead behavior.
- Implements sparse zero/punch operations and allocated-range queries using `SEEK_DATA`/`SEEK_HOLE`.
- Encodes and verifies NT security descriptor xattrs using NDR plus SHA-256 hashes of both NTSD and current POSIX ACL state.
- Encodes/decodes Samba-compatible DOS attribute xattrs for Windows attributes and creation time.
- Fills ksmbd stat wrappers with NT time conversion, allocation size, file attributes, and optional stored DOS attributes.
- Builds SMB stream xattr names using `user.DosStream.<name>:$DATA` or `:$INDEX_ALLOCATION`.
- Implements server-side copy chunk handling with access checks, lock checks, overlap fallback through splice, and cross-filesystem fallback.
- Initializes and inherits POSIX ACLs for new objects.

Dependencies:
- Uses VFS, xattr, POSIX ACL, NDR, SHA-256, oplock, stats, share config, session/user config, and ACL conversion helpers.

Role in subsystem:
- Main syscall-facing compatibility layer. It is where SMB file operations become safe Linux VFS operations while preserving Windows-visible metadata through xattrs.
