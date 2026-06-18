# sources/user-network-fs/libsmb2/examples/smb2-rename-sync.c

Purpose: This synchronous example renames a remote path within an SMB share.

Important APIs and types: It uses `smb2_connect_share`, `smb2_rename`, URL parsing, and cleanup APIs.

Control flow: The program expects a share URL plus source and destination path arguments, connects to the share, logs the rename operation, calls `smb2_rename`, disconnects, and exits.

State and persistence behavior: The persistent effect is remote namespace mutation on the SMB server.

Dependencies and integration points: It validates the high-level rename wrapper and server permissions/share mode handling.

Risks: Rename is destructive if the destination exists or if server semantics replace existing entries. Error exits skip some cleanup. Source and destination are raw argv strings, not normalized against URL path.

Test signals: Verify source disappears and destination appears with preserved content/metadata where expected. Test cross-directory rename, existing destination, missing source, and permission denied.
