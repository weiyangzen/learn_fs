# File Research: sources/os/linux/linux/fs/fhandle.c

Read status: complete, 474 lines.

Purpose: implements the Linux file-handle syscalls `name_to_handle_at()` and `open_by_handle_at()`, translating pathnames to exportfs file handles and decoding handles back into paths/files.

Key flow:
- `do_sys_name_to_handle()` validates exportfs support, copies the user `file_handle`, calls `exportfs_encode_fh()`, handles overflow/invalid handle return conventions, encodes connectable/directory user-visible type bits, and returns either legacy mount id or unique mount id.
- `name_to_handle_at()` validates `AT_*` flags, rejects conflicting `AT_HANDLE_CONNECTABLE` combinations, performs `filename_lookup()`, and delegates encoding.
- `handle_to_path()` copies and validates the user handle, anchors decoding to an fd, cwd, pidfs root, or nsfs root, runs filesystem-specific `export_operations.permission()` or `may_decode_fh()`, strips user flag bits, and calls `exportfs_decode_fh_raw()`.
- `open_by_handle_at()` decodes the handle and opens it via filesystem `eops->open()` or `file_open_root()`.

Important dependencies: `exportfs`, mount namespace helpers, fd RAII helpers, `CAP_DAC_READ_SEARCH`, `CAP_SYS_ADMIN`, idmapped mount checks, pidfs/nsfs root helpers, `FD_ADD()` file publishing.

Security/concurrency notes:
- Decoding permission is deliberately strict unless global `CAP_DAC_READ_SEARCH` is present.
- Relaxed decode requires `O_DIRECTORY`, mount/subtree checks, idmap reachability checks, and DAC override in the caller's user namespace.
- Connectable handles require subtree verification and directory-only constraints where encoded.
