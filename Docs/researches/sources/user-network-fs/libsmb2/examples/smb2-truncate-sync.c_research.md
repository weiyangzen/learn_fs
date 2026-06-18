# sources/user-network-fs/libsmb2/examples/smb2-truncate-sync.c

## Purpose
`smb2-truncate-sync.c` is a synchronous mutation example that resizes a remote SMB file to a user-supplied length. It demonstrates `smb2_truncate()` with the high-level connection flow.

## Important APIs, Types, and Functions
`main()` uses `smb2_init_context()`, `smb2_parse_url()`, `smb2_set_security_mode()`, `smb2_connect_share()`, `smb2_truncate()`, `smb2_disconnect_share()`, `smb2_destroy_url()`, and `smb2_destroy_context()`. The length is parsed with `strtoll(argv[2], NULL, 10)` and passed to the `uint64_t` length parameter.

## Control Flow
The program requires URL and length arguments, initializes and parses the SMB URL, enables signing capability, connects, calls `smb2_truncate(smb2, url->path, parsed_length)`, and then disconnects/free resources on success.

## State and Persistence Behavior
The only durable effect is remote file size modification. Local state is transient. Failed initialization, URL parsing, connection, or truncation exits leave process-local resources unfreed; truncation failure may still have remote-side partial effects depending on server semantics.

## Dependencies and Integration Points
It integrates with SMB `SET_INFO`/end-of-file behavior through the high-level libsmb2 API. It depends on server permissions that allow write attributes or file resize.

## Risks and Edge Cases
`strtoll()` errors are not checked; negative values are converted to a large unsigned length when passed to `smb2_truncate()`. Directory paths, read-only files, missing files, and share modes fail through libsmb2. The usage URL has the same extra `>` typo as the stat example.

## Test Signals
Test shrinking, extending, zero length, nonnumeric length, negative length, read-only files, directories, and locked files. Verify remote size with `smb2-stat-sync` or another client after each successful operation.
