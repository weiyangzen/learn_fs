# sources/user-network-fs/samba/source4/ntvfs/posix/posix_eadb.c

Purpose: provides a TDB-backed extended-attribute database for POSIX NTVFS deployments that cannot or do not use native xattrs. Attributes are keyed by device/inode plus attribute name and include a synthetic per-file list for cleanup.

Important APIs and functions: `get_ea_tdb_key` builds binary keys from `st_dev`, `st_ino`, and `attr_name`. Raw APIs are `pull_xattr_blob_tdb_raw`, `push_xattr_blob_tdb_raw`, `delete_posix_eadb_raw`, `unlink_posix_eadb_raw`, and `list_posix_eadb_raw`. `posix_eadb_add_list` maintains the special `.xattr_list` record. Under `WITH_NTVFS_FILESERVER`, wrapper functions route through `pvfs_state->ea_db`.

Control flow: reads stat/fstat the path or fd, fetch the key from TDB, and talloc-copy results. Writes create a temporary context, chain-lock the target key, update `.xattr_list` unless writing the list itself, then `tdb_store` the blob. Unlink reads `.xattr_list`, deletes each named attribute, and then deletes the list.

State and persistence: persistent state lives in the TDB database referenced by `struct tdb_wrap`. Keys follow files by inode/device, not path. The `.xattr_list` value is a packed NUL-separated string list used to remove orphaned records during unlink.

Dependencies and integration points: used by PVFS xattr hooks and exposed through `posix_eadb.h` prototypes. Depends on TDB, `stat`/`fstat`, Samba `DATA_BLOB`, and NTSTATUS error mapping.

Risks: keying by inode/device means replacement files get different keys while hard links share attributes; delete path uses fd `-1` for listed attributes during unlink, so path/inode state must still resolve; malformed `.xattr_list` could affect cleanup iteration; `tdb_chainlock` protects writes for one key but the list and attribute updates are not a wider transaction. Test signals include write/read/delete/list, hard-link behavior, unlink cleanup, missing file/status mapping, memory failures, and concurrent writers.
