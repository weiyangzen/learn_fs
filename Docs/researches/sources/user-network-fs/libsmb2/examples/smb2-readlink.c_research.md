# sources/user-network-fs/libsmb2/examples/smb2-readlink.c

Purpose: This synchronous example resolves a remote SMB reparse-point/symlink target.

Important APIs and types: It uses `smb2_connect_share`, `smb2_readlink`, fixed local buffer `char buf[256]`, and normal URL/context cleanup.

Control flow: The program parses an SMB URL, connects to the share, calls `smb2_readlink` on the path, prints either the target or the error string plus mapped errno text, then disconnects.

State and persistence behavior: It reads remote metadata only and persists nothing. Runtime state is the SMB context, parsed URL, and readlink buffer.

Dependencies and integration points: It exercises libsmb2's symlink/reparse-point handling through the public sync API.

Risks: The target buffer is fixed at 256 bytes, so long link targets may be truncated or fail depending on library behavior. It does not set user explicitly beyond URL parse/connect.

Test signals: Run against known symlinks/reparse points and normal files. Successful output should print `Link:<target>`, while non-links should produce a clear error.
