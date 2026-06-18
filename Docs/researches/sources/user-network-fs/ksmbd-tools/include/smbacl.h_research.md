<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/smbacl.h -->
# sources/user-network-fs/ksmbd-tools/include/smbacl.h

## Purpose

Declares SMB SID, ACL, ACE, and security descriptor helpers used by SAMR/LSARPC responses.

## Important APIs, Types, and Functions

Defines constants for SID authorities, ACE types, descriptor flags, SID type values, `struct smb_ntsd`, `struct smb_sid`, `struct smb_acl`, `struct smb_ace`, and helpers to read/write/copy/compare SIDs, initialize domain SIDs, build security descriptors, and resolve domain names.

## Control Flow

Service code uses these helpers to parse incoming SIDs, emit domain/user SIDs, and build self-relative security descriptors with DACLs.

## State and Persistence Behavior

No persistent state in the header. Implementations derive domain SID subauthorities from global configuration.

## Dependencies and Integration Points

Depends on linux types, GLib, rpc.h NDR helpers, and LSARPC domain constants.

## Risks and Edge Cases

SID subauthority bounds and descriptor size accounting are security-sensitive. Callers must supply valid DCE/RPC cursors and output buffers.

## Test Signals

Tests should read/write SIDs, compare SIDs, initialize domain SID from subauth, map known/unknown domains, and validate generated security descriptor layout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/smbacl.h -->
