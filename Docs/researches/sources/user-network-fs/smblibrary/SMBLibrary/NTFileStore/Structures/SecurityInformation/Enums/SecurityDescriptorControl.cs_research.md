<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/Enums/SecurityDescriptorControl.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/Enums/SecurityDescriptorControl.cs

## Purpose
Defines SECURITY_DESCRIPTOR_CONTROL bit flags such as DACL/SACL presence, inheritance state, protection, RM control, and self-relative layout.

## Important APIs, Types, And Functions
Declarations: `public enum SecurityDescriptorControl : ushort`. Enum values include `{`, `OwnerDefaulted = 0x0001`, `GroupDefaulted = 0x0002`, `DaclPresent = 0x0004`, `DaclDefaulted = 0x0008`, `SaclPresent = 0x0010`, `SaclDefaulted = 0x0020`, `DaclUntrusted = 0x0040`, `ServerSecurity = 0x0080`, `DaclAutoInheritedReq = 0x0100`, `SaclAutoInheritedReq = 0x0200`, `DaclAutoInherited = 0x0400`, `SaclAutoInherited = 0x0800`, `DaclProtected = 0x1000`. Specific behavior: it is stored on SecurityDescriptor and ORed with SelfRelative when writing.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/Enums/SecurityDescriptorControl.cs -->
