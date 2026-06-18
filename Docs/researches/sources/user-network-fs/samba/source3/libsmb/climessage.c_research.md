# sources/user-network-fs/samba/source3/libsmb/climessage.c

## Purpose

This file implements the legacy SMB "send message" client sequence. It starts a message to a destination host/user, sends the text in SMB-sized chunks, and terminates the message group.

## Important APIs, Types, and Functions

The public APIs are `cli_message_send()`, `cli_message_recv()`, and synchronous `cli_message()`. Internal helpers are `cli_message_start_send/recv`, `cli_message_text_send/recv`, and `cli_message_end_send/recv`. Their state structs carry the message group id, text word parameter, event context, CLI pointer, sent byte count, and original message pointer.

## Control Flow

`cli_message_send()` chains three SMB commands: `SMBsendstrt`, one or more `SMBsendtxt`, then `SMBsendend`. Start converts user and host from Unix to DOS charset and returns a group id if the server supplies one. Text chunks are limited to 127 bytes from the original message string; each chunk is converted to DOS charset if possible, otherwise sent in the Unix charset with a debug message. The sync wrapper creates a private event loop and rejects calls when other async calls exist.

## State and Persistence Behavior

The file keeps only request-local state. The durable side effect is remote server delivery of a legacy SMB message. The sent counter advances by source-string chunk length, not converted byte count, so state is tied to the input string boundaries.

## Dependencies and Integration Points

It depends on `cli_smb_send/recv`, tevent request helpers, charset conversion, and `smbXcli_conn_has_async_calls()`. It is a legacy SMB1 facility and does not branch to SMB2.

## Risks and Test Signals

Risks include charset conversion failures, repeated `strlen()` on mutable caller memory, chunking multi-byte input by source bytes, and ambiguous behavior when `SMBsendstrt` returns no group word. Tests should cover empty messages, >127-byte messages, conversion failures, missing group id, server errors at each phase, and sync rejection during active async traffic.
