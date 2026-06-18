# sources/user-network-fs/libsmb2/lib/smb2-cmd-query-info.c

## Purpose
Implements SMB2 QUERY_INFO request/reply encoding and fixed/variable response parsing for file, filesystem, security, and passthrough information classes.

## Important APIs, Types, And Functions
Core APIs are `smb2_encode_query_info_request`, `smb2_cmd_query_info_async`, `smb2_cmd_query_info_reply_async`, `smb2_process_query_info_fixed`, `smb2_process_query_info_variable`, `smb2_process_query_info_request_fixed`, and `smb2_process_query_info_request_variable`. It dispatches to file-info codecs such as `smb2_decode_file_all_info`, `smb2_encode_file_basic_info`, filesystem codecs such as `smb2_decode_file_fs_size_info`, and `smb2_decode_security_descriptor`.

## Control Flow
Client request encoding rejects non-empty input buffers, emits the fixed 41-byte request, stores `info_type` and `file_info_class` into the PDU for later unmarshalling, and pads the PDU. Reply encoding writes a fixed reply header, then chooses a typed encoder based on request `info_type` and `file_info_class`. Encoded output can be truncated to the caller's requested output length, in which case the PDU status is set to `SMB2_STATUS_BUFFER_OVERFLOW`. Receive parsing validates the fixed reply, detects offset plus length wraparound, rejects output beyond the SPL or into a chained PDU, and then decodes the variable buffer according to the remembered PDU query class.

## State And Persistence
PDU fields `info_type` and `file_info_class` are critical state because response decoding has no independent class marker. Decoded objects are allocated from the SMB2 context allocator, while passthrough output copies raw bytes into context-owned memory. Request parsing exposes input buffer bytes directly through `req->input`.

## Dependencies And Integration Points
This is the main bridge between raw QUERY_INFO commands and the structured file/filesystem/security descriptor codec files. It relies on PDU header state, `smb2->spl`, chained PDU `next_command`, passthrough mode, and status setting for buffer overflow.

## Risks
Most unsupported classes fail only after a reply arrives unless passthrough is enabled. Request encoding still lacks input-buffer support. Some decode paths allocate a type that may be broader than the decoded struct, and the stream info decoder intentionally over-allocates by payload size. Security info parsing is bypassed in passthrough mode.

## Test Signals
Cover every supported file and filesystem class, security descriptors, buffer overflow truncation, passthrough unknown classes, chained PDU boundary checks, wrapped output offsets, zero-length "No Info" replies, and malformed variable payload lengths.
