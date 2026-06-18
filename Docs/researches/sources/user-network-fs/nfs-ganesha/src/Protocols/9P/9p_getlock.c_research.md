## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_getlock.c

Purpose: parses `TGETLOCK` but currently acts as a placeholder.

APIs and flow: `_9p_getlock` decodes fid, lock type, range, proc id, and client id, validates fid bounds, then echoes the request lock fields in `RGETLOCK` without consulting state or FSAL locks.

State/dependencies: no persistent lock state is read or updated, and the actual fid lookup is commented out. It depends only on wire helpers and common error formatting.

Risks/tests: this is behaviorally incomplete for clients expecting fcntl-style conflict discovery. Tests should document the echo behavior and cover invalid fid; functional lock conflict tests should fail or be marked unsupported until implemented.
