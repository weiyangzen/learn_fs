# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_delete.c

This file implements legacy `SMB_COM_DELETE`, including single-file and wildcard deletion. It validates the path, resolves the parent directory, checks directory listing access, filters candidates by search attributes and DOS attributes, breaks oplocks, enforces share and byte-range conflict rules, and removes files through filesystem operations.

Entry points are `smb_pre_delete`, `smb_post_delete`, and `smb_com_delete`. Internal helpers are `smb_delete_single_file`, `smb_delete_multiple_files`, `smb_delete_find_fname`, `smb_delete_check_dosattr`, `smb_delete_remove_file`, `smb_delete_check_path`, and `smb_delete_error`.

`smb_pre_delete` decodes search attributes and path into `sr->arg.dirop.fqi`. `smb_com_delete` initializes and validates the pathname, performs delete-specific path checks, detects wildcards, reduces the path to parent directory and last component, validates the parent is a directory, rejects deleting `..` at the share root, checks `FILE_LIST_DIRECTORY` access on the parent, then dispatches to single or wildcard deletion. On success it returns an empty SMB response; on failure it uses the populated `smb_error_t`.

`smb_delete_single_file` validates the object name, performs a direct lookup in the parent directory, checks DOS attributes, calls the remove helper, and releases the file node. `smb_delete_multiple_files` opens an odir over the search path with broad search attributes, iterates matching names via `smb_odir_read`, does case-sensitive lookup of each returned name, applies delete-specific attribute filtering, and deletes candidates. Readonly matches abort with `NT_STATUS_CANNOT_DELETE`. Directory matches either end the search when directories were requested or are skipped through error handling. If no file is deleted, it reports `NT_STATUS_NO_SUCH_FILE`.

`smb_delete_check_dosattr` obtains DOS attributes with kcred and enforces SMB delete rules: directories are not deleted by this command, readonly files return cannot-delete, and hidden/system files are invisible unless the corresponding search attribute was requested. It also uses `SMB_PATHFILE_IS_READONLY`, so path-specific readonly behavior is respected.

`smb_delete_remove_file` performs the concurrency-sensitive removal. It first breaks delete-style oplocks with `smb_oplock_break_DELETE` and waits if necessary, then locks the node, checks delete/share state with `smb_node_delete_check`, enters an NBL critical section, checks `NBL_REMOVE` conflicts across the whole file range, applies CATIA flags when needed, and calls `smb_fsop_remove` using the node's parent and object name. Cleanup exits the critical section before returning.

`smb_delete_check_path` rejects missing final components as directory access errors and rejects `.` or wildcard patterns resolving to `.` when directory search attributes are involved. `smb_delete_error` is a small helper for consistent NT status plus DOS error class/code population.

Integration notes: this is SMB1 path-based deletion, not handle-based set-disposition deletion. It deliberately breaks oplocks before share and lock checks so clients holding batch/handle caching can flush or close before the server decides whether deletion is blocked. Wildcard deletion can skip transient not-found races after a directory entry is enumerated.
