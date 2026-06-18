<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/Enums/AceFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/Enums/AceFlags.cs

## Purpose
Defines ACE inheritance and audit flag bits for security descriptor ACE headers.

## Important APIs, Types, And Functions
Declarations: `public enum AceFlags : byte`. Enum values include `{`, `OBJECT_INHERIT_ACE = 0x01`, `CONTAINER_INHERIT_ACE = 0x02`, `NO_PROPAGATE_INHERIT_ACE = 0x04`, `INHERIT_ONLY_ACE = 0x08`, `INHERITED_ACE = 0x10`, `SUCCESSFUL_ACCESS_ACE_FLAG = 0x40`, `FAILED_ACCESS_ACE_FLAG = 0x80`. Specific behavior: it is a byte-sized [Flags] enum consumed by AceHeader and ACE serializers.

## Control Flow
Values are consumed by the security descriptor parser and ACE/ACL serializers. There is no branching beyond reading fixed-width fields and preserving bit flags.

## State And Persistence
State is limited to public value fields and computed lengths; there is no persistence beyond byte serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, plus adjacent `ACE`, `ACL`, `SID`, `AceType`, `AceFlags`, and `SecurityDescriptorControl` types. It integrates with SMB/NT file-store security information parsing and any file system code that transports Windows security descriptors.

## Risks
Bounds and validity checks are minimal, so malformed offsets, ACE sizes, SID subauthority counts, or ACL counts can surface as reader exceptions or inconsistent nested objects.

## Test Signals
Useful signals are byte-for-byte round trips for descriptors with owner, group, DACL, SACL, empty ACLs, multiple ACE sizes, Everyone/LocalSystem SIDs, all control flag combinations, and malformed offset/count fixtures that fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/Enums/AceFlags.cs -->
