# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/share_config.c

Read status: complete.

## Purpose
Caches and manages share configuration fetched from the ksmbd userspace IPC daemon.

## Main Responsibilities
- Hash share configs by casefolded share name and refcount cached entries.
- Request share metadata from userspace and validate returned share name.
- Parse share flags, masks, forced UID/GID, path, and veto patterns.
- Trim trailing slashes from share paths and resolve them with temporary fsuid/fsgid override.
- Support IPC pipe shares without backing path resolution.
- Handle stale share updates requested by userspace.
- Match filenames against per-share veto wildcard patterns.

## Dependencies And Role
Used by tree connect and VFS paths to map SMB share names to local paths and policy flags.

## Risks
Share path resolution runs under overridden credentials and must be reverted reliably. Payload sizing for veto list plus path is ABI-driven; malformed userspace data can otherwise corrupt share config state.
