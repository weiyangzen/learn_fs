<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/Enums/AceType.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/Enums/AceType.cs

## Purpose
Enumerates MS-DTYP ACE type identifiers for access allowed/denied, audit/alarm, object, callback, mandatory-label, resource-attribute, and scoped-policy ACEs.

## Important APIs, Types, And Functions
Declarations: `public enum AceType : byte`. Enum values include `{`, `ACCESS_ALLOWED_ACE_TYPE = 0x00`, `ACCESS_DENIED_ACE_TYPE = 0x01`, `SYSTEM_AUDIT_ACE_TYPE = 0x02`, `SYSTEM_ALARM_ACE_TYPE = 0x03`, `ACCESS_ALLOWED_COMPOUND_ACE_TYPE = 0x04`, `ACCESS_ALLOWED_OBJECT_ACE_TYPE = 0x05`, `ACCESS_DENIED_OBJECT_ACE_TYPE = 0x06`, `SYSTEM_AUDIT_OBJECT_ACE_TYPE = 0x07`, `SYSTEM_ALARM_OBJECT_ACE_TYPE = 0x08`, `ACCESS_ALLOWED_CALLBACK_ACE_TYPE = 0x09`, `ACCESS_DENIED_CALLBACK_ACE_TYPE = 0x0A`, `ACCESS_ALLOWED_CALLBACK_OBJECT_ACE_TYPE = 0x0B`, `ACCESS_DENIED_CALLBACK_OBJECT_ACE_TYPE = 0x0C`. Specific behavior: it is used by ACE.GetAce and AceHeader to choose or label concrete ACE records.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/Enums/AceType.cs -->
