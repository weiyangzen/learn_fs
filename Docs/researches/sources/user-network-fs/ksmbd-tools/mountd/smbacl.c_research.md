<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/smbacl.c -->
# sources/user-network-fs/ksmbd-tools/mountd/smbacl.c

## Purpose

Implements SID, ACL, and security descriptor helpers shared by SAMR and LSARPC.

## Important APIs, Types, and Functions

Important functions are `smb_read_sid`, `smb_write_sid`, `smb_copy_sid`, `smb_init_domain_sid`, `smb_compare_sids`, `set_domain_name`, `build_sec_desc`, plus internal ACE/DACL builders.

## Control Flow

SID read/write marshal revision, authority bytes, and subauthorities through NDR helpers. Domain SID initialization uses `global_conf.gen_subauth`. Domain-name resolution recognizes ksmbd's local domain, Unix users/groups SIDs, or falls back to SID string. Security descriptor building writes a self-relative descriptor with a DACL containing Everyone, Administrators, Account Operators, and owner RID ACEs.

## State and Persistence Behavior

No persistent state. It reads global subauth values and writes into the current DCE/RPC response payload.

## Dependencies and Integration Points

Depends on rpc.h NDR helpers, tools/global_conf, GLib, and LSARPC domain-name constants.

## Risks and Edge Cases

Subauthority count validation is critical. ACL size is patched after writing, so offset restoration must be exact. Access masks and RID constants are hard-coded and should match Windows expectations.

## Test Signals

Tests should round-trip SIDs, compare known SIDs, resolve local/unix/unknown domains, build security descriptors for sample RIDs, and verify ACL size and ACE count.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/smbacl.c -->
