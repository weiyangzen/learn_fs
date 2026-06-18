<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/SID.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/SID.cs

## Purpose
Represents a packet-format Windows SID with revision, six-byte identifier authority, and little-endian subauthority list.

## Important APIs, Types, And Functions
Declarations: `public class SID`. Constants: `public const int FixedLength = 8;`. Important fields include `public static readonly byte[] WORLD_SID_AUTHORITY = new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 }`, `public static readonly byte[] LOCAL_SID_AUTHORITY = new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00, 0x02 }`, `public static readonly byte[] CREATOR_SID_AUTHORITY = new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00, 0x02 }`, `public static readonly byte[] SECURITY_NT_AUTHORITY = new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00, 0x05 }`, `public byte Revision`, `public byte[] IdentifierAuthority`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it provides Everyone and LocalSystem helpers and fixed/computed length serialization.

## Control Flow
Construction reads revision, subauthority count, six authority bytes, then loops over little-endian subauthorities. Writing mirrors that sequence and derives the count from the list length.

## State And Persistence
State is limited to public value fields and computed lengths; there is no persistence beyond byte serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, plus adjacent `ACE`, `ACL`, `SID`, `AceType`, `AceFlags`, and `SecurityDescriptorControl` types. It integrates with SMB/NT file-store security information parsing and any file system code that transports Windows security descriptors.

## Risks
Bounds and validity checks are minimal, so malformed offsets, ACE sizes, SID subauthority counts, or ACL counts can surface as reader exceptions or inconsistent nested objects. IdentifierAuthority must be exactly six bytes and large subauthority counts can overflow byte count semantics if callers mutate the list unexpectedly.

## Test Signals
Useful signals are byte-for-byte round trips for descriptors with owner, group, DACL, SACL, empty ACLs, multiple ACE sizes, Everyone/LocalSystem SIDs, all control flag combinations, and malformed offset/count fixtures that fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/SID.cs -->
