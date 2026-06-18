# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_sd.c

## Purpose

`smb_sd.c` converts between Windows security descriptors and filesystem security structures. It reads filesystem owner/group/ACL data into an absolute SMB security descriptor, converts absolute SMB descriptors back to filesystem/ZFS ACL structures, maps SIDs to local ids and local ids to SIDs, and manages descriptor memory.

## Main Interfaces

- `smb_sd_init()` initializes an absolute security descriptor.
- `smb_sd_term()` frees owner, group, DACL, and SACL members.
- `smb_sd_len()` computes encoded security descriptor length for requested security information.
- `smb_sd_get_secinfo()` infers security information bits from a descriptor, used by create-with-SD.
- `smb_sd_read()` reads filesystem security and converts it to SMB form.
- `smb_sd_write()` converts SMB form to filesystem form and writes it.
- `smb_sd_tofs()` converts Windows SD owner/group/DACL/SACL into `smb_fssd_t`.
- `smb_fssd_init()` and `smb_fssd_term()` manage filesystem SD wrappers.

## Behavior And Data Flow

Reads initialize an `smb_fssd_t` with requested `secinfo` and directory flag, call `smb_fsop_sdread()`, then `smb_sd_fromfs()` builds an absolute Windows descriptor. Owner and group IDs are mapped to SIDs with `smb_idmap_getsid`; ZFS ACLs are converted to Windows ACLs with `smb_acl_from_zfs`; DACLs are sorted before returning to Windows clients; present/defaulted/auto-inherit/protected control bits are reconstructed from filesystem ACL flags.

Writes initialize an `smb_fssd_t`, call `smb_sd_tofs()`, and then `smb_fsop_sdwrite()`. Owner and group SIDs are validated and mapped to UID/GID with `smb_idmap_getid`. DACL and SACL conversion uses `smb_acl_to_zfs()` with flags derived from descriptor control bits and directory status. `EBADE` from filesystem write is mapped to `NT_STATUS_INVALID_OWNER`.

## Dependencies

This file depends on SMB filesystem SD operations, SMB/ZFS ACL conversion helpers, SMB SID validation and memory management, idmap, security descriptor control flags, and node type helpers.

## Notable Invariants And Risks

- `smb_sd_term()` assumes an absolute descriptor, not a self-relative descriptor.
- `secinfo` controls which descriptor parts the client intends to read or write; it also controls removal of present bits.
- Filesystem DACL cannot be absent in the same way Windows can represent it; the code treats a NULL DACL as equivalent to everyone-full for filesystem conversion.
- SID/idmap failures return `NT_STATUS_NONE_MAPPED` or `NT_STATUS_INVALID_SID`.
- DACL order matters to Windows GUI behavior, so DACLs are sorted on read.
- SACL handling preserves present/protected/auto-inherit-style flags but only converts when SACL is present.
