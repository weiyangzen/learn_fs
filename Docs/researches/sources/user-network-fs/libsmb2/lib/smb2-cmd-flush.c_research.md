<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-flush.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-flush.c

## Purpose

`smb2-cmd-flush.c` implements SMB2 FLUSH request and reply bodies, allowing clients to request that server-side cached file data for a file ID be committed.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_flush_async`, `smb2_cmd_flush_reply_async`, `smb2_process_flush_fixed`, and `smb2_process_flush_request_fixed`. Internal helpers encode fixed request and reply bodies. Payload type is `smb2_flush_request`.

## Control Flow

Request encoding writes struct size and file ID into a fixed body. Reply encoding writes only struct size. Parsers validate exact fixed body sizes; request parsing allocates a payload and copies the file ID.

## State And Persistence Behavior

No local persistence exists. The remote side may persist file data as a result of processing FLUSH, but this file only marshals the command.

## Dependencies And Integration Points

It integrates with file handle operations and the core PDU dispatcher. It relies on `SMB2_FD_SIZE` and endian/iovec helpers.

## Risks And Edge Cases

Failure paths after iovec allocation sometimes rely on generic cleanup and sometimes omit a specific error string. The command has no variable area, so malformed size handling is the main parser risk.

## Test Signals

Test file ID round-trip, fixed struct-size validation, successful server flush reply handling, error status routing through `smb2-cmd-error.c`, and full flush behavior against a server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-flush.c -->
