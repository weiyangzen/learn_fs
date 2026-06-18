# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_close.c

## Purpose
SMB2 server dispatch for `SMB2_CLOSE`.

## Key Function
- `smb2_close(...)`
  - Decodes close request:
    - structure size
    - flags
    - reserved
    - persistent and temporal FID
  - Looks up the FID before firing the DTrace start probe.
  - If `SMB2_CLOSE_FLAG_POSTQUERY_ATTRIB` is set, tries to fetch all attributes through `smb2_ofile_getattr`.
  - If attribute query fails, still closes the file and clears the postquery flag rather than failing close.
  - If durable handle is persistent, records persistent durable-handle close documentation state via `smb2_dh_setdoc_persistent`.
  - Closes the ofile with `smb_ofile_close`.
  - On success, encodes close response with timestamps, allocation size, file size, and DOS attributes.
  - On failure, emits SMB2 error response.

## Important Interactions
- Uses `smb2sr_lookup_fid` to resolve the open file.
- Uses `smb2_ofile_getattr` for optional post-close attributes.
- Uses durable-handle support when `of->dh_persist` is set.
- Close itself is not failed just because postquery attributes cannot be collected.

## Notes
- Response structure size is encoded as `60`, matching SMB2 close response format.
