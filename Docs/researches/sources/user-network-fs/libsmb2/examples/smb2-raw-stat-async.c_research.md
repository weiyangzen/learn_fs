# sources/user-network-fs/libsmb2/examples/smb2-raw-stat-async.c

Purpose: This raw async example retrieves `SMB2_FILE_ALL_INFORMATION` for a remote path using a compound request and prints detailed metadata.

Important APIs and types: It uses raw create/query-info/close requests, `SMB2_0_INFO_FILE`, `SMB2_FILE_ALL_INFORMATION`, `struct smb2_file_all_info`, access flag constants, file attribute constants, compound PDUs, `compound_file_id`, and poll-driven async completion.

Control flow: The program connects, sends compound CREATE/QUERY_INFO/CLOSE, waits for callback completion, checks status, then prints attributes, timestamps, allocation/end-of-file size, link count, delete-pending/directory flags, index number, EA size, access flags, current byte offset, mode flags, alignment requirement, and name.

State and persistence behavior: It opens and closes the remote object transiently and reads metadata only. Decoded metadata is freed through `smb2_free_data`.

Dependencies and integration points: It exercises libsmb2 raw metadata decoders and compound command sequencing, making it a strong integration example for lower-level users.

Risks: The mode printer checks `fs->access_flags` instead of `fs->mode`, which can mislabel mode flags. Many print paths assume decoded pointers are valid after successful status. Error handling exits without structured cleanup.

Test signals: Compare printed metadata against OS/server stat tools. Validate directory vs file paths, hidden/system/read-only attributes, sparse/compressed flags, and failure behavior for missing paths.
