# sources/user-network-fs/samba/source4/smb_server/smb/nttrans.c

## Purpose
Handles SMB1 NT transaction commands (`SMBnttrans` and `SMBnttranss`). It reconstructs potentially multi-packet NT transaction requests, dispatches transaction subcommands, calls NTVFS backends, marshals NT transaction replies, and fragments large replies across multiple SMB responses.

## Important APIs, Types, And Functions
- `struct nttrans_op` keeps the active transaction, backend operation object, and optional send marshaller.
- `smbsrv_reply_nttrans()` parses primary NT transaction headers, setup words, params, and data blobs.
- `smbsrv_reply_nttranss()` appends secondary params/data to a pending primary transaction.
- `reply_nttrans_complete()` wraps a reconstructed transaction in an NTVFS request and calls `nttrans_backend()`.
- `reply_nttrans_send()` runs any subcommand-specific send function, clamps output to requested max param/data sizes, and splits output into chunks.
- Subcommand parsers support `NT_TRANSACT_CREATE`, `IOCTL`, `RENAME`, `QUERY_SECURITY_DESC`, `SET_SECURITY_DESC`, and `NOTIFY_CHANGE`.
- Security descriptor paths use NDR helpers `ndr_pull_security_descriptor()` and `ndr_push_security_descriptor()`.

## Control Flow
The primary request parser validates word count, extracts max sizes, offsets, counts, setup count, and function ID, copies setup words, and range-checks params/data via `req_pull_blob()`. If totals exceed counts, `reply_nttrans_continue()` registers a `smbsrv_trans_partial` and sends an empty continue reply. Secondary packets are matched to a partial transaction, required to be contiguous by displacement, appended with `talloc_realloc()`, and discarded without a direct reply. Once totals are satisfied, the original request is completed through NTVFS. Async completion returns to `reply_nttrans_send()`, which invokes a subcommand send marshaller, builds the NT transaction response header, adds alignment padding, copies params/data, and clones the request for all but the last fragment.

## State And Persistence
Partial transaction state persists on `smb_conn->trans_partial` until complete or destroyed by `smbsrv_trans_partial_destructor()` from `trans2.c`. The primary request is retained as the owner of the partial state. Secondary packets update the primary request sequence number so the final response signs with the last secondary's sequence. Created file handles persist through the common SMB handle callback layer.

## Dependencies And Integration Points
Integrates with NTVFS operations: `ntvfs_open`, `ntvfs_qfileinfo`, `ntvfs_setfileinfo`, `ntvfs_rename`, `ntvfs_ioctl`, and `ntvfs_notify`. It shares partial transaction infrastructure and destructor with `trans2.c`, request parsing/string/blob helpers with `request.c` and `blob.c`, and handle validation with `smbsrv_pull_fnum()`.

## Risks
The secondary matching check only compares command and MID and includes a TODO to also check VUID, PID, and TID; cross-request confusion is the notable protocol-state risk. The flood limit allows more than 100 partials before rejecting, so resource pressure should be tested. Offset/count parsing is range-checked, but integer totals and realloc sizes are attack surface. `NTTRANS_CREATE` uses `MIN(fname_len+1, params.length - 53)` after a minimum-length check, so maintaining that guard is important. Notify response string sizing assumes a worst-case character multiplier and then shrinks to actual length.

## Test Signals
Exercise primary-only and secondary-completed NT transactions, non-contiguous secondary rejection, missing partial rejection, oversized response fragmentation, max-param/max-data truncation with `BUFFER_TOO_SMALL`, invalid setup counts, security descriptor NDR failures, handle validation for per-handle operations, notify-change async completion, and cancellation/connection cleanup of pending partials.
