# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_open_andx.c

## Summary
Implements legacy SMB1 open commands: `SMB_COM_OPEN`, `SMB_COM_OPEN_ANDX`, and `TRANS2_OPEN2`. These handlers translate old open-mode/ofun encodings into the common open path and encode legacy SMB1 responses.

## Main Responsibilities
- Decodes classic open and open-andx request formats.
- Converts SMB open mode to desired access and share access.
- Converts SMB open function to NT create disposition.
- Applies write-through and oplock request flags.
- Rejects or ignores legacy fields for Windows compatibility.
- Delegates actual open/create to `smb_common_open()`.
- Acquires SMB1 oplocks when requested.
- Encodes standard and extended legacy open responses.
- Rejects non-empty EA lists in `TRANS2_OPEN2`.

## Key APIs
- `smb_pre_open()`, `smb_post_open()`, `smb_com_open()`.
- `smb_pre_open_andx()`, `smb_post_open_andx()`, `smb_com_open_andx()`.
- `smb_com_trans2_open2()`.

## Important Behavior
`SMB_COM_OPEN` always uses `FILE_OPEN` and `FILE_NON_DIRECTORY_FILE`; it supports old SMB oplock flags from the SMB header and returns a 7-word response.

`OPEN_ANDX` ignores request search attributes for Windows compatibility, maps extended open flags to oplock and extended-response flags, handles creation time conversion, and encodes either 15-word or 19-word responses. Extended responses include max access and guest access.

`TRANS2_OPEN2` decodes transaction parameters, checks the data block for a non-empty EA list, and returns `NT_STATUS_EAS_NOT_SUPPORTED` when one is supplied. It clamps invalid create dispositions to `FILE_CREATE`.

## Dependencies
Depends on common open, SMB open-mode/share-mode conversion helpers, time conversion helpers, SMB1 oplock acquisition, ofile close on response failure, and transaction mbuf encoding.

## Risks
`sm b_open_dsize_check` is a tunable defaulting to disabled, so oversized legacy allocation sizes are normally passed through common open logic after 32-bit protocol truncation in responses.

`TRANS2_OPEN2` accepts only an empty EA payload; clients depending on EAs receive an explicit unsupported status.
