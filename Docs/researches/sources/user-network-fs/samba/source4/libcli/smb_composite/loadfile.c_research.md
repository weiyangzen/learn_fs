<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/loadfile.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/loadfile.c

Purpose: implements an async whole-file read over SMB1 using open, repeated ReadX, and close.

Important APIs and types: `enum loadfile_stage`, `struct loadfile_state`, `smb_composite_loadfile_send`, `smb_composite_loadfile_recv`, `smb_composite_loadfile`, `loadfile_open`, `loadfile_read`, `loadfile_close`, and `setup_close`. It depends on raw open/read/close requests.

Control flow: `send` opens `io->in.fname` with `RAW_OPEN_NTCREATEX`, read-data access, shared read/write, normal attributes, and anonymous impersonation. On open completion it rejects files larger than 100 MB, allocates `io->out.data`, and either closes zero-length files or starts 32 KiB ReadX chunks. Each read advances the offset and output pointer until the expected size is reached, then closes the handle.

State and persistence: the only persistent result is an in-memory buffer and size stolen to the caller in recv. The remote handle should always be closed on normal paths; errors during open/read may leave closure to lower transport/server cleanup.

Risks: no retry logic and no short-read guard except completion by offset plus bytes read; a zero-byte read before expected size could loop if the server reports success with no data. The 100 MB cap is a hard resource policy. Test signals include zero-length files, boundary sizes around 32768 and 100 MB, short read behavior, open denial, and close failure propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/loadfile.c -->
