<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawfile.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawfile.c

Purpose: `rawfile.c` implements SMB1 raw file namespace, open, close, lock, flush, checkpath, and seek operations. It is the low-level packet builder/parser for many `union smb_open`, `smb_rename`, `smb_mkdir`, `smb_close`, `smb_lock`, `smb_flush`, and `smb_seek` levels.

Important APIs, types, and functions: Key entry points include `smb_raw_rename_send/smb_raw_rename`, `smb_raw_unlink_send/smb_raw_unlink`, `smb_raw_mkdir_send/smb_raw_mkdir`, `smb_raw_rmdir_send/smb_raw_rmdir`, `smb_raw_open_send/smb_raw_open_recv/smb_raw_open`, `smb_raw_close_send/smb_raw_close`, `smb_raw_lock_send/smb_raw_lock`, `smb_raw_chkpath_send/smb_raw_chkpath`, `smb_raw_flush_send/smb_raw_flush`, and `smb_raw_seek_send/smb_raw_seek_recv/smb_raw_seek`. Local helpers handle `TRANSACT2_MKDIR`, `TRANSACT2_OPEN`, and `NT_TRANSACT_CREATE`.

Control flow: Most functions switch on the union's `generic.level`, build the corresponding SMB command with `smbcli_request_setup`, fill VWV fields and data strings/blobs, send, then receive and parse level-specific reply words. Open has the richest flow: old open, OpenX, mknew/create/ctemp/splopen, NTCreateX, trans2 open, NTTRANS create, and chained OpenX/ReadX or NTCreateX/ReadX. Chained opens call `smbcli_chained_request_setup` and `smbcli_chained_advance` to parse the read response after open metadata.

State and persistence behavior: The file creates and destroys transient requests but changes server-side state: rename/unlink/mkdir/rmdir mutate namespace, open returns file handles, close releases handles, locks affect byte-range locking state, flush commits server buffers, and seek returns a server-calculated offset. It relies on `tree->session->transport->negotiate.capabilities` for large-file offsets and date conversion.

Dependencies and integration points: It depends on raw request helpers, trans2/nttrans helpers, EA serialization, NDR security descriptor encoding, DOS date helpers, and raw read parsing for chained reads. Higher-level `clifile`, torture raw tests, NTVFS CIFS passthrough, and client commands integrate with these calls.

Risks: SMB2 levels return `NULL` here, so callers must route SMB2 elsewhere. Many branches assume the matching union branch is initialized correctly. Chained read output buffers must be allocated by the caller before receive. The code has multiple wire-offset constants; mistakes break interoperability. Some allocation failures in helper paths return `NULL` after allocating temporary contexts, and packet growth invalidates local pointers.

Test signals: `source4/torture/raw/open.c`, `unlink.c`, `seek.c`, `oplock.c`, lock tests, and basic namespace tests exercise this file. Important coverage includes large-file offsets with and without `CAP_LARGE_FILES`, chained open-read bounds checks, ctemp returned names, NTTRANS create with EAs/security descriptors, flush-all, and malformed WCT replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawfile.c -->
