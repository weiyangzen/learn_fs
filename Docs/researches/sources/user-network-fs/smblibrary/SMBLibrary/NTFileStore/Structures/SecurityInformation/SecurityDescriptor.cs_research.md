<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/SecurityDescriptor.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/SecurityDescriptor.cs

## Purpose
Models a self-relative SECURITY_DESCRIPTOR containing optional owner SID, group SID, SACL, and DACL sections.

## Important APIs, Types, And Functions
Declarations: `public class SecurityDescriptor`. Constants: `public const int FixedLength = 20;`. Important fields include `public byte Revision`, `public byte Sbz1`, `public SecurityDescriptorControl Control`, `public SID OwnerSid`, `public SID GroupSid`, `public ACL Sacl`, `public ACL Dacl`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods. Specific behavior: it parses header offsets, materializes optional nested SID/ACL objects, and writes a compact self-relative descriptor.

## Control Flow
Construction reads the fixed descriptor header, then follows non-zero owner/group/SACL/DACL offsets into nested SID or ACL objects. Writing first computes all self-relative offsets from the fixed header, writes the header with `SelfRelative` set, then emits optional sections in owner, group, SACL, DACL order. No external state is consulted.

## State And Persistence
State is an in-memory descriptor graph of optional owner/group SIDs and SACL/DACL ACLs plus control bits. Serialization is self-contained and does not persist outside the returned byte array.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, plus adjacent `ACE`, `ACL`, `SID`, `AceType`, `AceFlags`, and `SecurityDescriptorControl` types. It integrates with SMB/NT file-store security information parsing and any file system code that transports Windows security descriptors.

## Risks
Bounds and validity checks are minimal, so malformed offsets, ACE sizes, SID subauthority counts, or ACL counts can surface as reader exceptions or inconsistent nested objects. Only self-relative layout is written; callers expecting absolute descriptors must not reuse this serializer blindly.

## Test Signals
Useful signals are byte-for-byte round trips for descriptors with owner, group, DACL, SACL, empty ACLs, multiple ACE sizes, Everyone/LocalSystem SIDs, all control flag combinations, and malformed offset/count fixtures that fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/SecurityDescriptor.cs -->
