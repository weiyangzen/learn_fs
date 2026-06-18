<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-lock.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-lock.c

## Purpose

`smb2-cmd-lock.c` implements SMB2 byte-range lock request and reply marshalling. It supports one inline lock element in the fixed body and additional lock elements in the variable area.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_lock_async`, `smb2_cmd_lock_reply_async`, `smb2_process_lock_fixed`, `smb2_process_lock_request_fixed`, and `smb2_process_lock_request_variable`. Internal helpers include `smb2_encode_lock_request`, `smb2_encode_lock_reply`, and `smb2_parse_locks`. Important types are `smb2_lock_request` and `smb2_lock_element`.

## Control Flow

Request encoding writes lock count, packed sequence number/index, file ID, first lock element, and optional extra elements. Reply encoding writes only struct size. Fixed request parsing validates size, unpacks sequence fields, copies file ID, requires at least one lock, allocates a lock array, parses the inline element, and returns the byte count for remaining locks. Variable parsing parses the remaining elements.

## State And Persistence Behavior

Local state is transient in PDU payloads. Remote state can create, unlock, or fail byte-range locks on the server. Parsed locks are allocated from the libsmb2 context allocator.

## Dependencies And Integration Points

The file depends on PDU helpers, endian accessors, and lock constants from libsmb2 headers. It integrates with file APIs that expose SMB2 locking.

## Risks And Edge Cases

The encoder allocates space for `lock_count` elements in the variable iovec even though the first element is already in the fixed body; it only fills `lock_count - 1`, leaving extra padded space. Fixed parsing constructs a temporary iovec starting at `iov->buf + SMB2_LOCK_ELEMENT_SIZE`; this works because the first lock starts at offset 24 and `SMB2_LOCK_ELEMENT_SIZE` is 24, but it is non-obvious. Large `lock_count` can drive large allocation without an explicit cap.

## Test Signals

Test one-lock and multi-lock requests, sequence packing/unpacking, invalid zero lock count, large lock counts, lock/unlock/shared/exclusive flags, malformed variable lengths, and server-visible byte-range lock behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-lock.c -->
