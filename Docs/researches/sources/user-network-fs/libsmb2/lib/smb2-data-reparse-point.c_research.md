# sources/user-network-fs/libsmb2/lib/smb2-data-reparse-point.c

## Purpose
Decodes SMB2 reparse data buffers, currently handling symbolic-link reparse payloads.

## Important APIs, Types, And Functions
The file exports `smb2_decode_reparse_data_buffer`, operating on `struct smb2_reparse_data_buffer` and `struct smb2_iovec`.

## Control Flow
The decoder checks for the reparse header, reads `reparse_tag` and `reparse_data_length`, verifies the declared data fits, and switches on the tag. For `SMB2_REPARSE_TAG_SYMLINK`, it reads symlink flags, substitute-name offset/length, and print-name offset/length. Each UTF-16 name is converted to UTF-8 and allocated under the reparse buffer object.

## State And Persistence
Decoded symlink names are stored inside the caller-provided reparse structure using context allocation. No encode path or global state exists.

## Dependencies And Integration Points
This decoder is consumed by higher-level FSCTL or QUERY_INFO paths that retrieve reparse data. It depends on iovec getters, UTF conversion, and context allocation.

## Risks
The function does not check UTF conversion return before `strlen(tmp)`, so malformed UTF-16 can crash. Only symlinks are interpreted; other reparse tags are accepted with just the tag and length populated. Offset arithmetic uses 16-bit fields and should be fuzzed for wrap/edge cases.

## Test Signals
Cover valid symlink substitute and print names, relative/absolute flags, unknown tags, short headers, declared lengths beyond the buffer, malformed UTF-16, and offset-plus-length boundary cases.
