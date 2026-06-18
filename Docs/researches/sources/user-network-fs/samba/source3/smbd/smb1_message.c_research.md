<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_message.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_message.c

## Purpose
`smb1_message.c` implements legacy SMB1 winpopup-style messaging commands: `SMBsends`, `SMBsendstrt`, `SMBsendtxt`, and `SMBsendend`. These commands collect sender, recipient, and message text from SMB1 requests and deliver the text by writing it to a temporary file and executing the configured `message command`.

## Important APIs, types, and functions
`struct msg_state` holds `from`, `to`, and accumulated `msg` strings. `msg_deliver()` is the central delivery routine: it verifies that `lp_message_command()` is configured, creates a secure temporary file under `tmpdir()` using `mkstemp()` with group/other permissions masked, converts message data from DOS to UNIX codepage when possible, writes the message while collapsing CRLF to LF-style output, substitutes `%f`, `%t`, `%s`, and standard Samba variables into the configured command, then executes it with `smbrun()`.

The public SMB handlers are `reply_sends()` for one-shot messages, `reply_sendstrt()` to begin a multi-part message, `reply_sendtxt()` to append a fragment, and `reply_sendend()` to deliver and clear the accumulated state.

## Control flow
`reply_sends()` checks that a message command is configured, allocates a temporary `msg_state` on `talloc_tos()`, decodes ASCII `from` and `to` strings from `req->buf + 1`, reads a two-byte message length and clamps it to the remaining request buffer, copies the payload, calls `msg_deliver()`, and returns an empty SMB1 success response.

The multi-part path stores state on `req->xconn->smb1.msg_state`. `reply_sendstrt()` frees any prior state, creates a new `msg_state` under the connection, and decodes sender/recipient. `reply_sendtxt()` validates that state exists and the request has at least a length field, clamps the supplied fragment length, `talloc_realloc()`s the accumulated message buffer, appends bytes, and replies success. `reply_sendend()` validates state, calls `msg_deliver()`, frees the connection message state, and replies success.

Each handler uses SMB profile counters and maps missing configuration to `NT_STATUS_REQUEST_NOT_ACCEPTED`; malformed sequencing or too-short buffers return `NT_STATUS_INVALID_PARAMETER`; allocation failure returns `NT_STATUS_NO_MEMORY`.

## State and persistence behavior
One-shot delivery stores message state only for the current request. Multi-part delivery persists partial message state in `xconn->smb1.msg_state` across SMB requests on the same SMB1 connection until `reply_sendend()` or a new `reply_sendstrt()` frees it. Delivery creates a temporary file and leaves lifecycle behavior to the external message command and system temp cleanup; the code does not unlink the file after `smbrun()`.

## Dependencies and integration points
The module depends on SMB1 request parsing helpers (`srvstr_pull_req_talloc()`, `smbreq_bufrem()`), talloc ownership, loadparm substitution, character conversion (`convert_string_talloc()`), filesystem temp creation, `smbrun()`, profile macros, and the `smbXsrv_connection` SMB1 state block. It is invoked from the SMB1 command dispatch table, not from SMB2.

## Risks and edge cases
The largest security risk is command execution: although sender and recipient are filtered through `alpha_strcpy()`, the configured `message command` receives substituted values and a temp-file path. Administrators must treat it as trusted configuration. The temp file is created with restricted permissions but not explicitly removed. Message accumulation uses talloc buffer size as the current length; repeated `SMBsendtxt` fragments can grow memory until normal request/resource limits intervene. `reply_sends()` and `reply_sendtxt()` clamp payload length to the request buffer, which is important for malformed clients.

Conversion fallback intentionally delivers DOS codepage bytes if conversion fails. CRLF handling skips carriage returns when followed by line feed but writes all other bytes one at a time, so very large messages incur many writes. Multi-part sequencing is strict: `sendtxt` or `sendend` without `sendstrt` returns invalid parameter.

## Test signals
Tests should cover no `message command`, one-shot and multi-part delivery, repeated `sendstrt` state replacement, `sendtxt` before start, short buffers, over-declared message lengths, codepage conversion failure fallback, CRLF normalization, temp-file creation failure, and command substitution of sender, recipient, current user/domain, and temp path. Resource tests should verify accumulated message length behavior under many fragments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_message.c -->
