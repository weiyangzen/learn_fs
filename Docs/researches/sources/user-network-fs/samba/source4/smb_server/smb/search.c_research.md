# sources/user-network-fs/samba/source4/smb_server/smb/search.c

## Purpose
Implements legacy SMB directory search commands (`SMBsearch`, `SMBffirst`, `SMBfunique`) and `SMBfclose`. This predates Trans2 search and uses fixed 43-byte result entries plus 21-byte resume keys.

## Important APIs, Types, And Functions
- `struct search_state` carries the active request and minimal callback state.
- `find_fill_info()` appends one 43-byte legacy search result to the output data if it fits `req_max_data()`.
- `find_callback()` adapts NTVFS search callbacks to the legacy result formatter.
- `smbsrv_reply_search()` parses first/next style requests and chooses `RAW_SEARCH_SEARCH`, `RAW_SEARCH_FFIRST`, or `RAW_SEARCH_FUNIQUE`.
- `reply_search_first_send()` and `reply_search_next_send()` write the returned entry count.
- `smbsrv_reply_fclose()` parses a resume key and calls `ntvfs_search_close()`.

## Control Flow
The search handler requires WCT 2, parses an ASCII4 pattern, then requires a type-5 variable block containing a resume key length. It prebuilds a one-word reply with an empty variable block. If resume key length is zero, it starts `ntvfs_search_first()` with search attributes and max count. If a 21-byte resume key is present, it rejects `SMBfunique`, decodes the legacy ID fields, and calls `ntvfs_search_next()`. Backend callbacks append entries until the output would exceed negotiated reply capacity. `SMBfclose` requires an empty pattern plus a 21-byte resume key and maps it to `RAW_FINDCLOSE_FCLOSE`.

## State And Persistence
Legacy search state itself is backend-owned; the frontend only serializes and returns the resume key fields supplied by NTVFS. No long-lived frontend search object is stored here. The output data grows per returned entry under the request context.

## Dependencies And Integration Points
Depends on request parsing/growth helpers, DOS time serialization from `srvtime.c`, and NTVFS search operations. It is dispatched from `receive.c` for command bytes 0x81-0x84 and coexists with Trans2 findfirst/findnext in `trans2.c`.

## Risks
The fixed legacy structures have strict sizes and weak typing. Incorrect resume key validation can desynchronize client and backend search state. Result truncation is callback-driven; count returned by the backend must match entries actually serialized. Names are copied into a 12-byte padded field, so short-name formatting and null termination behavior are compatibility-sensitive.

## Test Signals
Test search first, search next with a valid 21-byte key, invalid block type, invalid key lengths, `SMBfunique` with resume key rejection, max transmit truncation, empty pattern requirements for fclose, and backend errors in async callbacks.
