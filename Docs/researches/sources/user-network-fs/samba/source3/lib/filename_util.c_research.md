# sources/user-network-fs/samba/source3/lib/filename_util.c

Purpose: manipulates, copies, formats, validates, and splits `struct smb_filename` values and related stream/EA names.

Important APIs/types/functions: full-name/debug helpers, synthetic/copy helpers, no-stream copy, stream predicates, EA validation, and `split_stream_filename()`.

Control flow: constructors build temporary filename structures and deep-copy them with pooled talloc storage. Debug formatting appends `@GMT` timestamp text when present. Stream checks enforce invariants before classifying named/default streams. Split separates at the first colon.

State/persistence behavior: no global state. Returned filename objects own base/stream copies plus stat, flags, and timestamp fields.

Dependencies/integration: used broadly by smbd VFS and path operations while handling NTFS streams and POSIX paths.

Risks/test signals: stream parsing and invariant enforcement are security-sensitive. Tests should cover base-only names, named/default streams, invalid empty stream names, POSIX paths, timestamp debug strings, invalid EA characters, and allocation failure.
