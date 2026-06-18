# sources/user-network-fs/libsmb2/examples/smb2-cat-async.c

Purpose: This example asynchronously reads a remote SMB file and writes it to stdout.

Important APIs and types: It uses `smb2_init_context`, `smb2_parse_url`, `smb2_set_security_mode`, `smb2_connect_share_async`, `smb2_open_async`, `smb2_pread_async`, `smb2_close_async`, `smb2_disconnect_share_async`, `smb2_get_fd`, `smb2_which_events`, `smb2_service`, and POSIX `poll`/`write`. A global buffer and position track reads.

Control flow: Connect callback opens the file, open callback starts a read at offset zero, read callback writes bytes to stdout and queues the next read, and EOF triggers async close and disconnect. The main loop polls the libsmb2 fd until the disconnect callback sets `is_finished`.

State and persistence behavior: Runtime state is a global 256 KiB buffer, `pos`, `is_finished`, and the file handle passed through callbacks. The program writes only stdout and does not persist local files.

Dependencies and integration points: It demonstrates libsmb2's async file API and its integration with a manual poll loop. It includes Amiga/AROS poll compatibility stubs.

Risks: The read size constant is 102400 while the buffer is larger. Error branches often call `exit`, skipping normal SMB cleanup. `write` errors abort. The callback chain assumes the file handle remains valid until close.

Test signals: Reading a known remote file should produce byte-for-byte stdout output and exit after disconnect. Network failures, EOF, and permission errors validate callback status handling.
