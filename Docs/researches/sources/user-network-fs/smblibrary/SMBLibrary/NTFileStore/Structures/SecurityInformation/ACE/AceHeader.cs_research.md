<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AceHeader.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AceHeader.cs

## Purpose
Models the four-byte MS-DTYP ACE_HEADER prefix used before every access-control entry.

## Important APIs, Types, And Functions
Declarations: `public class AceHeader`. Constants: `public const int Length = 4;`. Important fields include `public AceType AceType`, `public AceFlags AceFlags`, `public ushort AceSize`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it reads AceType, AceFlags, and AceSize from the buffer and writes them back in little-endian form.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AceHeader.cs -->
