# sources/user-network-fs/libsmb2/examples/smb2-stat-sync.c

## Purpose
`smb2-stat-sync.c` is a synchronous command-line example that connects to an SMB share and prints POSIX-like metadata for one SMB URL path. It demonstrates the high-level `libsmb2.h` synchronous connection, URL parsing, and `smb2_stat()` API.

## Important APIs, Types, and Functions
`usage()` prints the expected `smb://[domain;][user@]host[:port]/share/path` form and exits. `main()` uses `smb2_init_context()`, `smb2_parse_url()`, `smb2_set_security_mode(SMB2_NEGOTIATE_SIGNING_ENABLED)`, `smb2_connect_share()`, `smb2_stat()`, `smb2_disconnect_share()`, `smb2_destroy_url()`, and `smb2_destroy_context()`. The result is read from `struct smb2_stat_64`, including `smb2_type`, `smb2_size`, `smb2_ino`, link count, and four timestamp fields.

## Control Flow
The program validates that a URL argument was supplied, initializes a context, parses the URL into server/share/user/path fields, enables signing capability, connects to the share, calls `smb2_stat()` for `url->path`, switches over the returned SMB2 file type, prints scalar metadata and formatted local-time timestamps, then disconnects and destroys allocated URL/context state.

## State and Persistence Behavior
All state is transient process memory inside the libsmb2 context, parsed URL, and stack `smb2_stat_64`. It does not persist files or modify the share. On several error paths it exits without destroying the URL/context, which is acceptable for a short-lived example but not a pattern for long-running tools.

## Dependencies and Integration Points
It depends on libc formatting/time APIs, `smb2.h`, `libsmb2.h`, and `libsmb2-raw.h`. The operational integration point is any reachable SMB2/SMB3 server with credentials encoded in the URL or resolved by libsmb2 defaults.

## Risks and Edge Cases
The usage string has an extra `>` after host in the URL example. `asctime(localtime())` can return NULL on invalid timestamps and is locale/timezone dependent. Exit code `0` is used for init/parse failures, while connection/stat failures use `10`. The program enables signing as supported but does not require signing.

## Test Signals
Run against files, directories, missing paths, permission-denied paths, and servers with unusual timestamps. Check printed type mapping, 64-bit size/inode formatting, cleanup under success, and failure messages from `smb2_get_error()`.
