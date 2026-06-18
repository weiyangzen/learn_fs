# sources/user-network-fs/samba/source4/smb_server/smb/trans2.c

## Purpose
Implements SMB1 `SMBtrans`, `SMBtranss`, `SMBtrans2`, and `SMBtranss2` handling. It reconstructs multi-packet transaction requests, passes named `SMBtrans` calls to NTVFS, implements Trans2 subcommands for filesystem/file info, open, mkdir, directory search, set info, and DFS referrals, marshals replies, and fragments large transaction responses.

## Important APIs, Types, And Functions
- `struct trans_op` stores request, transaction, command, backend object, and optional send marshaller.
- `reply_trans_generic()` parses primary transaction requests; `reply_transs_generic()` appends secondary chunks.
- `reply_trans_complete()` dispatches either `ntvfs_trans()` or `trans2_backend()`.
- `reply_trans_send()` serializes and fragments transaction replies.
- `trans2_backend()` first offers direct passthrough via `ntvfs_trans2()`, then handles specific setup subcommands.
- File/fs info helpers: `trans2_push_fsinfo()`, `trans2_push_fileinfo()`, `trans2_parse_sfileinfo()`.
- Search helpers: `struct find_state`, `find_fill_info()`, `trans2_findfirst()`, `trans2_findnext()`.
- `trans2_getdfsreferral()` implements DFS referral lookup and NDR marshaling.
- `smbsrv_trans_partial_destructor()` removes partial transaction records from the connection list.

## Control Flow
Primary transaction parsing validates WCT, totals, max sizes, setup count, setup words, optional transaction name, and param/data blobs. Incomplete requests are stored on `smb_conn->trans_partial` and receive an empty continue response. Secondary requests are matched by command and MID, required to be contiguous by displacement, appended to the primary blobs, and freed without reply. On completion, an NTVFS request is created. Trans2 dispatch handles direct backend implementation first; otherwise setup word zero selects DFS referral, findfirst/findnext, qpath/qfile info, setfile/setpath info, qfsinfo, open, or mkdir. Async completion marshals params/data, applies status if needed, and chunks according to negotiated max transmit with SMB transaction alignment padding.

## State And Persistence
Partial transactions persist under the primary request until complete. Secondary packets update the primary request signing sequence. Directory search handles are backend state; the frontend keeps only per-call callback state and last-entry offsets for resume reporting. DFS referral processing opens SAM DB context transiently. Open and mkdir operations may create persistent backend/file state via NTVFS.

## Dependencies And Integration Points
Depends on NTVFS, raw protocol structures, SMB blob helpers, EA parsing/writing, passthrough info/search marshaling in `blob.c`, DFS NDR generated code, SAM DB, auth system session, loadparm DFS settings, and request/signing infrastructure. It shares partial-transaction storage with `nttrans.c`.

## Risks
Like NTTrans, secondary matching only checks command and MID and has a TODO for VUID/PID/TID. Transaction totals are 16-bit in Trans2, but realloc and copy paths still need malformed-length coverage. `trans2_getdfsreferral()` can produce large blobs and has logic to trim referrals only in the 56 KiB max-response case. File-info level mapping accepts many passthrough levels while explicitly rejecting unsupported Unix and special levels; level regressions are common compatibility risks. Search callback truncates by rolling back the last entry when output exceeds `max_data`, so counts and last offsets must match serialized data.

## Test Signals
Cover primary-only and secondary transaction assembly, non-contiguous secondary rejection, partial flood limit, response fragmentation and alignment, direct `ntvfs_trans2()` passthrough, each implemented Trans2 subcommand, EA list parsing and output, unsupported info levels, DFS referral disabled/enabled/oversized behavior, findfirst/findnext truncation at `max_data`, setfile rename/disposition/allocation/EOF parsing, and signing sequence across secondary completion.
