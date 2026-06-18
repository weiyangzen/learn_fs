# File Research: sources/os/linux/linux/fs/smb/client/smb2misc.c

This file contains SMB2/SMB3 miscellaneous protocol helpers: response validation, SMB2 length calculation, data-area discovery, path conversion, lease-state conversion, oplock/lease-break dispatch, cancelled-open cleanup, cancelled-close retry, and SMB3.1.1 preauth hash updates.

Primary responsibilities:
- Validate SMB2 response headers and fixed structure sizes.
- Calculate expected SMB2 response lengths and tolerate documented server padding quirks.
- Locate variable-length data areas for SMB2 response types.
- Convert CIFS paths to SMB2 UTF-16 paths, trimming leading separators where required.
- Translate CIFS cache/oplock flags into SMB2 lease-state flags.
- Match server oplock/lease break notifications to open files, pending opens, or cached directory handles.
- Queue async lease-break acknowledgements and cancelled-handle closes.
- Maintain SMB3.1.1 preauthentication integrity hash.

Important control flow:
- `check_smb2_hdr()` verifies protocol ID, message ID, and response direction, with an exception for server oplock-break requests.
- `smb2_check_message()` validates header size, command range, maximum buffer size, response `StructureSize2`, calculated length, negotiate-context length, and known compatibility exceptions.
- `get_neg_ctxt_len()` validates SMB3.1.1 negotiate context count/offset and returns negotiate-context plus padding length.
- `smb2_get_data_area_len()` extracts response-specific offset/length fields for negotiate, session setup, create, query info, read, query directory, ioctl, and change notify.
- `smb2_calc_size()` combines SMB2 header size, fixed response body size, and variable data-area length while rejecting overlapping data offsets.
- `smb2_is_valid_oplock_break()` handles classic FID-based oplock breaks and delegates 44-byte lease breaks to `smb2_is_valid_lease_break()`.
- Lease-break matching walks sessions and tcons on the primary server, checks open files, pending opens, and cached directories, then queues the proper oplock-break or lease-break work.
- `smb2_handle_cancelled_mid()` schedules an async close if a successful SMB2 CREATE response arrives for an interrupted MID and the command was not already a create-close compound.
- `smb311_update_preauth_hash()` updates the session preauth SHA-512 hash for negotiate and relevant session setup packets.

Validation and compatibility:
- The response-size table mirrors expected SMB2 response `StructureSize2` values by command.
- Error packets with SMB2 error structure size are allowed where fixed sizes otherwise mismatch.
- Special cases tolerate symlink create errors with extra data, Windows 7 oplock-break padding, implied one-byte BCC differences, 8-byte compound padding, and macOS write-response junk padding.
- Data-area offsets are bounded to `4096` and lengths to `128 KiB`; invalid offset/length pairs cause the data area to be ignored.
- Cancelled close retry checks tcon refcount and skips async close if the tree connection is already closing.

Dependencies:
- SMB2 PDU structures, CIFS session/tcon/open-file lists, cached directory lease handling, workqueues, tracepoints, SHA-512 crypto, SMB2 close/lease-break helpers, and SMB3 dialect/session state.

Research notes:
- This is the main SMB2 receive-side sanity checker and asynchronous notification router.
- The validation code balances strict structure checks with practical exceptions for real server behavior.
- Lease-break handling is concurrency-sensitive because it walks global session/tcon state while coordinating open-file locks and pending-open state.
