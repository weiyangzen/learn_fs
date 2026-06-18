<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/pdu.c -->
# sources/user-network-fs/libsmb2/lib/pdu.c

## Purpose

`pdu.c` is the central SMB2 packet lifecycle module. It allocates PDUs, initializes SMB2 headers, encodes and decodes fixed header fields, manages compound chains, selects tree/session IDs, correlates server replies with queued requests, dispatches fixed and variable payload parsing to command-specific files, applies signing/encryption decisions, and times out queued commands.

## Important APIs, Types, And Functions

Key exported helpers are `smb2_allocate_pdu`, `smb2_queue_pdu`, `smb2_free_pdu`, `smb2_add_compound_pdu`, `smb2_get_compound_pdu`, `smb2_decode_header`, integer endian accessors, tree ID helpers, message-id accessors, `smb2_find_pdu`, fixed-size lookup functions, payload dispatcher functions, and `smb2_timeout_pdus`. The file works on `struct smb2_context`, `struct smb2_pdu`, `struct smb2_header`, `struct smb2_io_vectors`, and `struct smb2_iovec`.

## Control Flow

Allocation creates a zeroed PDU, fills protocol magic, command, credit charge/request, tree ID, session ID, seal flag, timeout, and a first output iovec for the SMB2 header. Queueing walks each compound PDU, server-side correlates replies and sets flags, encodes headers, optionally signs each PDU, encrypts the chain, then appends it to the outqueue and updates events. Receive processing is split: `smb2_get_fixed_size` chooses the fixed body length, then fixed and variable dispatchers call command-specific parsers.

## State And Persistence Behavior

There is no disk persistence. Runtime state is in context queues, `message_id`, `async_id`, `credits`, tree-id stack, session ID, current input header, and PDU payload pointers. Timeouts invoke the original callback with `SMB2_STATUS_IO_TIMEOUT` and free the PDU. Compound metadata preserves previous compound message IDs for client receive ordering.

## Dependencies And Integration Points

The module depends on libsmb2 private headers, endian helpers, list macros, signing, and SMB3 sealing. Every `smb2-cmd-*` file plugs into this dispatcher through `smb2_process_*` functions. Socket integration is through `smb2_write_to_socket`, `smb2_change_events`, and `smb2_which_events`.

## Risks And Edge Cases

Tree-id state is global to the context and is mutated while decoding server-side requests, so concurrent or nested use must be serialized. `smb2_queue_pdu` uses `pdu` rather than loop variable `p` in several server-side flag/message-id checks, which is worth testing for compound replies. The endian setters use direct casts for 16/32-bit writes and may be sensitive to unaligned access on strict platforms. Error-response classification treats selected warnings as errors and special-cases `STATUS_MORE_PROCESSING_REQUIRED`.

## Test Signals

Test header encode/decode against captured SMB2 frames, compound `next_command` and related-operation flag updates, client message-id increments for credit charge, server reply correlation including async `STATUS_PENDING`, tree connect reply tree-id handling, unsolicited oplock breaks, signing/encryption hooks, dispatch tables for every command, and timeout removal from both outqueue and waitqueue.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/pdu.c -->
