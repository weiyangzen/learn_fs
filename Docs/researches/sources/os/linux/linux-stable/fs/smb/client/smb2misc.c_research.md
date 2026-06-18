# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2misc.c

## Purpose
Implements SMB2/SMB3 miscellaneous protocol validation and support helpers: response structure validation, size calculation, path conversion, lease/oplock break handling, cancelled-command cleanup, and SMB3.1.1 preauth hash updates.

## Main Responsibilities
- Validate SMB2 headers and response structure sizes.
- Calculate SMB2 message sizes from fixed and variable-length areas.
- Handle SMB3.1.1 negotiate-context length accounting.
- Convert CIFS paths to SMB2 UTF-16 path strings.
- Derive lease state from CIFS inode caching flags.
- Process server oplock and lease break notifications.
- Queue close work for cancelled opens/closes to avoid server handle leaks.
- Update SMB3.1.1 preauthentication integrity hash.

## Key Functions
- `check_smb2_hdr()` validates protocol ID, message ID, response flag, and allows oplock-break requests from the server.
- `get_neg_ctxt_len()` computes SMB3.1.1 negotiate context length, including padding/SPNEGO layout validation.
- `smb2_check_message()` validates full SMB2 response framing: transform header handling, header structure size, command range, fixed response size, calculated length, padding exceptions, symlink create exception, and max length.
- `smb2_get_data_area_len()` returns variable data offset/length for commands with data areas.
- `smb2_calc_size()` computes expected SMB2 frame size from header, fixed parameter area, and variable data area.
- `cifs_convert_path_to_utf16()` strips leading slash/backslash when required and converts to UTF-16 using mount charset/remapping.
- `smb2_get_lease_state()` converts CIFS cache/oplock flags into SMB2 lease-state bits.
- `smb2_is_valid_oplock_break()` handles classic oplock break messages and delegates lease breaks when structure size indicates a lease break.
- `smb2_is_valid_lease_break()` searches sessions/tcons/open files/pending opens/cached dirs for a matching lease key and queues appropriate break handling.
- `smb2_cancelled_close_fid()` performs async close for handles left open after interrupted operations.
- `smb2_handle_cancelled_close()` safely takes a tcon ref and queues close retry for interrupted close.
- `smb2_handle_cancelled_mid()` queues close retry for successful create responses whose MID was cancelled before normal processing.
- `smb311_update_preauth_hash()` updates session preauth SHA-512 hash for negotiate/session-setup traffic as required by SMB3.1.1.

## Important Tables and Structures
- `smb2_rsp_struct_sizes[]` maps each SMB2 command to expected response `StructureSize2`.
- `has_smb2_data_area[]` marks which SMB2 commands include variable response data.
- `struct smb2_lease_break_work` carries lease break ack work to `cifsiod_wq`.

## Important Data Flow
- Incoming SMB2 frames are validated by protocol ID, MID, command, fixed structure size, and computed variable payload length.
- Lease/oplock breaks are correlated through tcon open-file lists, pending-open lists, and cached directory lease state.
- Cancelled create/close recovery captures persistent/volatile FIDs and asynchronously closes them on the server.
- Preauth hashing chains the prior hash with each relevant request/response iov.

## Edge Cases and Defensive Logic
- Accepts known server padding quirks, including compound 8-byte padding, Windows oplock extra bytes, implied BCC byte behavior, and macOS write-response padding.
- Treats SMB2 transform frames specially to locate matching sessions before decryption handling.
- Rejects impossible data offsets/lengths with conservative limits.
- Skips preauth update after final successful session setup response.
- Avoids async close retry when tcon refcount indicates the tree is closing.
- Handles lease breaks for pending opens by queueing a separate lease-break ack worker after dropping locks.
