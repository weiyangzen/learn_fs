# sources/user-network-fs/libsmb2/examples/smb2-server-sync.c

Purpose: This example implements a minimal synchronous SMB2 server using libsmb2 server callbacks, primarily as a protocol harness rather than a real filesystem server.

Important APIs and types: It defines `struct smb2_server_request_handlers`, `struct smb2_server`, and handlers for authorization, session, tree connect/disconnect, create, close, flush, read, write, lock, ioctl, cancel, echo, query directory, and query info. It uses server helpers such as `smb2_serve_port`, `smb2_set_version`, `smb2_register_error_callback`, `smb2_utf8_to_utf16`, and many SMB2 reply structs.

Control flow: `main` sets signing and anonymous access, assigns a port, and calls `smb2_serve_port`. New clients are configured by `on_new_client`. Request handlers synthesize fixed responses: a disk or pipe share type, normal file attributes, a 32-byte read payload, write count echoing input length, fixed directory entries, and selected file/filesystem info structures.

State and persistence behavior: The server is stateless and does not persist file data. Query directory uses a static counter to alternate between two-entry output and end-of-directory. Allocated response buffers are handed to the server framework for response encoding/freeing.

Dependencies and integration points: It exercises libsmb2's server-side API, decoder/encoder paths, authentication hooks, signing, named-pipe share detection, and client compatibility against synthetic file data.

Risks: This is not a secure or complete server. Anonymous access is enabled, file data is synthetic, directory info construction is minimal, and some allocations on error are not fully unwound. `fill_dir_info` sets names as string pointers after UTF-16 conversion work, so correctness depends on server encoders' expectations.

Test signals: Connect a libsmb2 or OS SMB client to the chosen port, list the share, read the synthetic file, query metadata, and verify handlers produce stable replies. Server logs should show selected dialect and client errors.
