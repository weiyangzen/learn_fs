# File Research: sources/os/linux/linux/fs/smb/server/smb_common.c

Implements protocol negotiation, common SMB request validation, directory pseudo-entry population, 8.3 short-name generation, share-mode checks, credential override, and generic access mapping.

Key behaviors:
- Defines supported SMB dialect tables for SMB1 negotiate upgrade paths and SMB2/SMB3 dialect IDs.
- Negotiates dialects from both SMB1-style dialect strings and SMB2 dialect ID arrays, respecting `server_conf.min_protocol` and `server_conf.max_protocol`.
- Validates inbound SMB frames, rejecting unsupported compression transform requests and non-SMB protocol IDs.
- Provides minimal SMB1 negotiate support solely to upgrade clients to SMB2+ negotiation; SMB1 commands otherwise return invalid/no response.
- Populates `"."` and `".."` directory entries through caller-provided query-dir formatting callbacks.
- Generates DOS 8.3 short names using uppercased basename/extension plus checksum mangling.
- Enforces SMB share-mode compatibility across existing opens on the same ksmbd inode, including delete/read/write sharing and stream-file distinctions.
- Overrides/reverts kernel credentials to a session/share fsuid/fsgid and supplementary groups before VFS operations.
- Maps SMB generic desired access bits to concrete file access masks.

Dependencies:
- Depends on connection, work, session, user, tree connect, share config, VFS, Unicode conversion, and SMB2 handler code.
- Consumes `server_conf` and connection ops/values to initialize dialect-specific server behavior.

Role in subsystem:
- Provides the common control-plane glue between raw SMB negotiation, ksmbd connection state, Windows access semantics, and Linux credentials.
