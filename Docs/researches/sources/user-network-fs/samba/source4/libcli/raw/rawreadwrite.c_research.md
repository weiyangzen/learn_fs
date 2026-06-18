<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawreadwrite.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawreadwrite.c

Purpose: `rawreadwrite.c` implements raw SMB1 file read and write operations across old commands, lock/read, readbraw, ReadX, write-unlock, write, write-close, WriteX, and spool write.

Important APIs, types, and functions: Public entry points are `smb_raw_read_send`, `smb_raw_read_recv`, `smb_raw_read`, `smb_raw_write_send`, `smb_raw_write_recv`, and `smb_raw_write`. They operate on `union smb_read`, `union smb_write`, raw request setup/send/receive helpers, `smbcli_raw_pull_data`, and negotiated capabilities such as `CAP_LARGE_FILES` and `CAP_LARGE_READX`.

Control flow: Read send switches by level, builds the appropriate SMB command and word count, encodes file number/count/offset/remaining fields, adds high offset words for large-file capable servers, and optionally sets `FLAGS2_READ_PERMIT_EXECUTE`. Read receive validates WCT, extracts byte counts and offsets, handles large ReadX replies that exceed 64 KiB under `CAP_LARGE_READX`, validates output size against requested min/max, and copies data into caller-provided buffers. Write send builds data blocks or direct WriteX payloads, copies caller data into the request, and sends. Write receive validates reply WCT and extracts written counts, including high bits for WriteX.

State and persistence behavior: Reads do not mutate remote file content, though lockread may combine lock semantics at the server. Writes mutate server-side file data and may update metadata. The file stores no state beyond request lifetime; all read data lands in caller-owned output buffers.

Dependencies and integration points: It depends on `rawrequest.c` for packet buffers and bounds checking, `rawdate.c` for write-close mtime encoding, and negotiate state for large offsets. Raw open chained read logic in `rawfile.c` mirrors the ReadX parser. Torture raw read/write suites and client file wrappers are primary consumers.

Risks: Callers must allocate output buffers large enough for requested read sizes. ReadBraw uses `MAX(parms->readx.in.mincnt, parms->readx.in.maxcnt)` while in the `readbraw` branch, relying on union layout compatibility; that is fragile. Large offset TODO notes that the code does not error when a 64-bit offset is requested without server support. SMB2 levels return `NULL` or internal error here.

Test signals: Raw read/write torture tests should cover all levels, zero-byte operations, large offsets with and without `CAP_LARGE_FILES`, `CAP_LARGE_READX` oversize replies, read-for-execute flags, short replies, write count high bits, write-close mtime, and invalid SMB2 level handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawreadwrite.c -->
