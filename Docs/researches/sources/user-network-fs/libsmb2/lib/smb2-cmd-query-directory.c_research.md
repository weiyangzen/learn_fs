# sources/user-network-fs/libsmb2/lib/smb2-cmd-query-directory.c

## Purpose
Implements SMB2 QUERY_DIRECTORY request/reply construction and parsing, plus a decoder for `FILE_ID_FULL_DIRECTORY_INFORMATION`. It supports both client-side directory enumeration requests and server-style reply/request handling.

## Important APIs, Types, And Functions
The exported entry points are `smb2_cmd_query_directory_async`, `smb2_cmd_query_directory_reply_async`, `smb2_process_query_directory_fixed`, `smb2_process_query_directory_variable`, `smb2_process_query_directory_request_fixed`, and `smb2_process_query_directory_request_variable`. `smb2_decode_fileidfulldirectoryinformation` decodes a single directory entry into `struct smb2_fileidfulldirectoryinformation`. The code depends on `struct smb2_query_directory_request`, `struct smb2_query_directory_reply`, `struct smb2_fileidbothdirectoryinformation`, iovec helpers, and UTF-16/UTF-8 conversion helpers.

## Control Flow
Client request encoding allocates the fixed request buffer, writes information class, flags, file index, file id, name offset/length, and output buffer length, then appends an optional UTF-16 search pattern. `smb2_cmd_query_directory_async` pads the outgoing chain and sets `credit_charge` for large output buffers when multi-credit is supported. Reply encoding can either pass a raw server buffer through or convert an in-memory list of `smb2_fileidbothdirectoryinformation` records into packed `FILE_ID_FULL_DIRECTORY_INFORMATION` or `FILE_ID_BOTH_DIRECTORY_INFORMATION` entries with `next_entry_offset` chaining. Receive-side parsing validates fixed sizes, checks variable buffer bounds and overlap against the SMB2 header, then stores a pointer into the final receive iovec.

## State And Persistence
State is carried in allocated PDU payloads and in iovec-backed variable buffers. Request names decoded from inbound server requests are copied into the SMB2 context allocator with `smb2_alloc_init`, so the pointer survives beyond the temporary input iovec. The function does not persist directory enumeration state itself; file id, flags, and file index come from caller/server state.

## Dependencies And Integration Points
This file integrates with the generic PDU allocator, 64-bit padding, credit accounting, SMB2 fixed/variable payload dispatch, Unicode conversion, and FILEID directory info structures from `libsmb2-private.h`. It is used by raw directory enumeration APIs and by server/pass-through paths that synthesize query-directory replies.

## Risks
The reply encoder has multiple allocation-error paths where already-added iovectors rely on later PDU cleanup. Unsupported directory information classes result in zero-sized entries rather than a specific protocol error. `smb2_decode_fileidfulldirectoryinformation` validates `name_len` with a redundant-looking overflow guard and should be fuzzed with extreme lengths. Server request parsing checks filename bounds, but some conversions assume valid UTF-16 input.

## Test Signals
Exercise empty and non-empty search names, both supported info classes, passthrough replies, multi-entry chaining, zero-length output replies, malformed name offsets, output buffers that overlap fixed headers, and multi-credit output lengths above 64 KiB.
