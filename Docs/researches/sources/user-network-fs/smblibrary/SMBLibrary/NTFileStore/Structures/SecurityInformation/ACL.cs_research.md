<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACL.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACL.cs

## Purpose
Represents a self-contained access control list as a List<ACE> with ACL revision, reserved fields, computed size, and ACE count.

## Important APIs, Types, And Functions
Declarations: `public class ACL : List<ACE>`. Constants: `public const int FixedLength = 8;`. Important fields include `public byte AclRevision`, `public byte Sbz1`, `public ushort Sbz2`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it parses ACEs sequentially with ACE.GetAce and serializes list length/count before each ACE.

## Control Flow
Construction reads ACL revision/reserved/size/count, advances past the fixed header, then loops `AceCount` times using each ACE header size to locate the next ACE. Writing emits computed total length and count before delegating serialization to each ACE.

## State And Persistence
State is limited to public value fields and computed lengths; there is no persistence beyond byte serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, plus adjacent `ACE`, `ACL`, `SID`, `AceType`, `AceFlags`, and `SecurityDescriptorControl` types. It integrates with SMB/NT file-store security information parsing and any file system code that transports Windows security descriptors.

## Risks
Bounds and validity checks are minimal, so malformed offsets, ACE sizes, SID subauthority counts, or ACL counts can surface as reader exceptions or inconsistent nested objects.

## Test Signals
Useful signals are byte-for-byte round trips for descriptors with owner, group, DACL, SACL, empty ACLs, multiple ACE sizes, Everyone/LocalSystem SIDs, all control flag combinations, and malformed offset/count fixtures that fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACL.cs -->
