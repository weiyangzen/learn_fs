# sources/user-network-fs/libsmb2/lib/smb2-cmd-set-info.c

## Purpose
Builds SMB2 SET_INFO requests/replies and parses inbound SET_INFO requests, supporting selected file information classes and passthrough raw buffers.

## Important APIs, Types, And Functions
Primary entry points are `smb2_cmd_set_info_async`, `smb2_cmd_set_info_reply_async`, `smb2_process_set_info_fixed`, `smb2_process_set_info_request_fixed`, and `smb2_process_set_info_request_variable`. It uses `smb2_encode_file_basic_info`, `struct smb2_file_end_of_file_info`, `struct smb2_file_disposition_info`, and `struct smb2_file_rename_info`.

## Control Flow
Request encoding writes the fixed SET_INFO header, file id, and buffer offset. In passthrough mode it appends caller-supplied raw data. Structured mode supports `SMB2_FILE_BASIC_INFORMATION`, EOF size changes, rename, and disposition/delete-pending. Rename names are converted from UTF-8 to UTF-16 and forward slashes are converted to backslashes. Reply encoding emits an empty fixed success structure. Request parsing stores fixed fields and returns `buffer_length`; variable parsing currently only exposes raw input in passthrough mode.

## State And Persistence
The request payload owns no persistent server-side decoded structures in non-passthrough mode; server parsing rejects interpretation unless passthrough is set. Rename and metadata values are serialized into PDU iovectors. File id and additional information are carried in `struct smb2_set_info_request`.

## Dependencies And Integration Points
This file depends on file-info encoders, Unicode conversion, PDU padding, and pass-through server logic. Higher-level filesystem APIs call it for chmod/timestamps/truncate/rename/delete style operations.

## Risks
Passthrough mode sets fields on the current iovec after appending the raw buffer, so header field writes can target the appended buffer rather than the fixed header. Request parsing returns `buffer_length` without validating `buffer_offset` or header overlap. Non-passthrough server interpretation is intentionally absent. The typo in an error string is harmless but signals limited coverage of unsupported paths.

## Test Signals
Test basic info, EOF, rename with slash conversion, disposition, passthrough raw buffers, unsupported info classes, malformed buffer offsets, zero-length buffers, and server request parsing in both passthrough and structured modes.
