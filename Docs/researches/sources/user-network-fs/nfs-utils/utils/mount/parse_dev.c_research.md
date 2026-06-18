# sources/user-network-fs/nfs-utils/utils/mount/parse_dev.c

Purpose: parses an NFS device string into server hostname/address and export pathname.

Important APIs: `nfs_parse_devname(devname, hostname, pathname)` is exported. Internal parsers handle standard `host:path`, bracketed IPv6 `[addr]:path`, and reject `nfs://` URLs with a clear error.

Control flow: the public parser duplicates the input because parsing is destructive. Standard parsing splits at the first colon and truncates unsupported replicated-host lists at the first comma with a warning. Bracket parsing requires a closing `]` followed by `:`. Both paths enforce hostname and pathname length limits and allocate requested output strings.

State and persistence: no persistent state; output strings are caller-owned heap allocations.

Dependencies and integration: uses nfs-utils `nfs_error`, gettext wrappers, and global `progname`. Included where string mount/unmount parsing needs robust host/path extraction.

Risks: the simple-host parser contains an unusual `else` attachment before path parsing but effectively continues for no-comma cases; replicated mounts and NFS URLs are intentionally unsupported. Test signals include null input, missing colon, overlong host/path, replicated host warnings, bracketed IPv6 success/missing-brace failure, and allocation cleanup on partial failure.
