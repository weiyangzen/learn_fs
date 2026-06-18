# sources/user-network-fs/libsmb2/examples/smb2-cat-sync.c

Purpose: This synchronous example reads a remote SMB file and writes it to stdout.

Important APIs and types: It uses `smb2_init_context`, `smb2_parse_url`, `smb2_connect_share`, `smb2_open`, `smb2_pread`, `smb2_close`, `smb2_disconnect_share`, and cleanup APIs. It uses a 16 MiB static buffer and tracks the read offset in `pos`.

Control flow: The program parses the URL, connects, opens the path read-only, loops on `smb2_pread`, retries on `-EAGAIN`, writes successful reads to stdout, then closes and disconnects.

State and persistence behavior: State is only in memory and stdout. No local files are modified.

Dependencies and integration points: It exercises the blocking wrapper API, which internally drives the async service loop. It is a simple utility-style test for read correctness.

Risks: The 16 MiB static buffer is large for constrained systems. Some early error exits skip cleanup. Partial stdout writes are not handled beyond checking for negative return.

Test signals: Compare stdout to the source file content. Exercise EOF, `-EAGAIN`, missing path, and permission-denied cases.
