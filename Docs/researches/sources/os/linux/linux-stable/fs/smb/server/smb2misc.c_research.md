# File Research: sources/os/linux/linux-stable/fs/smb/server/smb2misc.c

This file validates incoming SMB2-family request framing, fixed structure sizes, variable data areas, compound message lengths, and credit charges. It also routes SMB2 negotiate to the common negotiate handler.

Validation tables:
- `smb2_req_struct_sizes[]`
  - Expected `StructureSize2` per SMB2 command.
  - Includes special handling note for oplock/lease break.
- `has_smb2_data_area[]`
  - Marks which SMB2 commands have variable data areas that need offset/length validation.

Functions:
- `check_smb2_hdr()`
  - Rejects packets marked `SMB2_FLAGS_SERVER_TO_REDIR`, since incoming requests must not be server-to-client responses.

- `smb2_get_data_area_len()`
  - Extracts variable data offset/length by command:
    - session setup security buffer
    - tree connect path
    - create name and create contexts
    - query/set info buffers
    - read/write channel/data buffers
    - query directory filename
    - lock element array
    - ioctl input buffer
  - Caps offsets over 4096 and total offset+length over `MAX_STREAM_PROT_LEN`.

- `smb2_calc_size()`
  - Computes expected SMB2 PDU size from SMB2 header, fixed structure size, and variable data area.
  - Adjusts lock request size because its structure size includes one lock element.
  - Rejects variable data that overlaps the fixed area.

- Request/response length helpers:
  - `smb2_query_info_req_len()`
  - `smb2_set_info_req_len()`
  - `smb2_read_req_len()`
  - `smb2_write_req_len()`
  - `smb2_query_dir_req_len()`
  - `smb2_ioctl_req_len()`
  - `smb2_ioctl_resp_len()`

- `smb2_validate_credit_charge()`
  - Computes required credit charge from the larger of request length and expected response length.
  - Requires at least one credit.
  - Rejects credit charge above connection max credits.
  - Under `credits_lock`, rejects requests exceeding granted or outstanding credits, otherwise increments outstanding credits.

- `ksmbd_smb2_check_message()`
  - Validates compound `NextCommand` bounds.
  - Adjusts current length for compounded or offset SMB2 message.
  - Rejects response-direction messages, bad SMB2 header structure size, invalid command index, and bad command fixed structure size.
  - Handles special oplock break structure sizes.
  - Ensures fixed request structure fits.
  - Compares calculated length against actual length, allowing:
    - one-byte implied BCC variance
    - 8-byte compound padding
    - negotiate validation deferral
    - up to 8 bytes of padding seen from some clients
  - Validates large-MTU credit charge when enabled.

- `smb2_negotiate_request()`
  - Calls `ksmbd_smb_negotiate_common()` for SMB2 negotiate.

Dependencies:
- SMB2 PDU structures and constants.
- Connection credit state.
- Common negotiate path.

Risk areas:
- This is a primary network-input validation boundary; offset, length, and credit rules protect later command handlers.
- Credit accounting increments `outstanding_credits` during validation; downstream response-credit handling must balance this correctly.
- Create-context bounds are only partially checked here; `smb2_find_context_vals()` performs deeper create-context validation later.
- Accepted padding exceptions are compatibility-sensitive; tightening them can break clients, loosening them can expose parser confusion.
