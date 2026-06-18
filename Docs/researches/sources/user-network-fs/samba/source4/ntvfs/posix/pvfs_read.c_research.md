# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_read.c

Purpose: `pvfs_read.c` implements file reads for the POSIX NTVFS backend, primarily the generic `RAW_READ_READX` path after older SMB read levels have been mapped by common ntvfs code.

Important APIs, types, and functions: The single exported function is `pvfs_read`. It works with `union smb_read`, `struct pvfs_file`, `struct pvfs_file_handle`, byte-range lock checks, and either POSIX `pread` or `pvfs_stream_read`.

Control flow: Non-READX levels are delegated to `ntvfs_map_read`. READX finds the backend handle with `pvfs_find_fd`, rejects directories or invalid devices where `fd == -1`, builds the required access mask from `SEC_FILE_READ_DATA` and optional execute-read semantics, validates the handle grant, rejects overly large SMB1 read counts, checks byte-range locks with `pvfs_check_lock`, then reads from an alternate stream or POSIX fd. SMB2 honors `mincnt`: short reads below `mincnt`, or EOF with a nonzero request length, return `NT_STATUS_END_OF_FILE`. Successful reads update both `position` and `seek_offset` to offset plus bytes read.

State and persistence behavior: Reads do not persist metadata. They mutate only handle-local current position fields. Stream reads load stream blobs from xattr/EADB state through the stream layer.

Dependencies and integration points: It depends on open handle lookup, security masks from generated security headers, strict byte-range lock enforcement, stream storage helpers, POSIX errno mapping, and protocol version from the request context.

Risks: SMB1 and SMB2 size/minimum-count behavior differs. Stream reads materialize blob data rather than using a native file descriptor, so large streams depend on xattr/EADB limits and memory behavior. Correct lock range checking is critical to Windows semantics.

Test signals: Exercise SMB1 and SMB2 reads, read-for-execute access, denied read masks, directory-handle reads, locked ranges, max-count validation for SMB1, EOF/mincnt handling, and alternate data stream reads.
