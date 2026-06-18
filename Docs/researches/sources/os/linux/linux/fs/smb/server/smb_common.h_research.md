# File Research: sources/os/linux/linux/fs/smb/server/smb_common.h

Declares common protocol identifiers, SMB1 negotiate structures, access-mask expansions, version operation tables, and shared helper APIs.

Key contents:
- Protocol indexes from SMB1 through SMB 3.1.1 and `BAD_PROT`.
- SMB open-result constants and generic read/write/execute/all access-mask definitions.
- SMB1 negotiate response struct and SMB flag constants used for SMB1 negotiate upgrade.
- Common directory info structs and server version dispatch tables: `smb_version_ops` and `smb_version_cmds`.
- Prototypes for dialect lookup, message validation, server initialization, dot entry population, short-name extraction, negotiation, share-mode checks, fsid override, server-side copy limits, wildcard checks, and generic access mapping.
- Inline `smb_get_msg()` helper to skip the 4-byte RFC1002 header.

Role in subsystem:
- Central header that lets connection/request code call version-specific SMB handlers through common ops while sharing access and negotiation helpers.
