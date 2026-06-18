# sources/user-network-fs/samba/source4/libcli/climessage.c

## Purpose

`climessage.c` implements legacy SMB messenger commands for starting, sending, and ending a message sequence to a host/user through an SMB tree connection.

## Important APIs, Types, and Functions

The public functions are `smbcli_message_start()`, `smbcli_message_text()`, and `smbcli_message_end()`. They manually build `SMBsendstrt`, `SMBsendtxt`, and `SMBsendend` requests with `smbcli_request_setup()`.

## Control Flow

Start appends username and host strings, sends and receives the request, checks tree error state, and returns the message group id from the response. Text sends the group id plus raw message bytes. End sends the group id to close the message sequence. Each path destroys the request on completion or failure.

## State and Persistence Behavior

Remote state is the server-side message group/session between start and end. Local state is only the returned integer group id. No persistent files are touched.

## Dependencies and Integration Points

It depends on low-level SMB request construction, string/byte append helpers, request send/receive, `smbcli_is_error()`, and SMB command constants.

## Risks and Edge Cases

This is legacy protocol functionality and may be unsupported by modern servers. The text function accepts a mutable `char *` even though it only sends bytes. Errors are collapsed to boolean false, so callers need tree error state for details.

## Test Signals

Tests require a server that supports messenger commands. Useful checks cover start/text/end success, invalid group ids, unsupported server responses, zero-length text, and non-ASCII message bytes.
