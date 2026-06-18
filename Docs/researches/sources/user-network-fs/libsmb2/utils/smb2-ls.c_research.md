<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/utils/smb2-ls.c -->
# sources/user-network-fs/libsmb2/utils/smb2-ls.c

Purpose: Command-line SMB directory listing utility using synchronous libsmb2 APIs.

Important APIs, types, and functions: Defines `usage` and `main`; uses URL parsing, `smb2_connect_share`, `smb2_opendir`, `smb2_readdir`, `smb2_readlink`, and cleanup calls.

Control flow: Connects to the share, opens the URL path as a directory, prints each entry name/type/size/mtime, resolves link targets, then closes/disconnects.

State and persistence behavior: Transient context, URL, directory handle, and temporary link strings. No persistence.

Dependencies and integration points: Depends on libsmb2 sync API and is used by tests, including filename discovery for the credit stress test.

Risks: Output format is human-oriented and scripts parse it with simple tools, making changes risky. Link target buffer is fixed at 256 bytes.

Test signals: Exercised by tests indirectly and useful as a manual integration tool.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/utils/smb2-ls.c -->
