<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntry.cs

## Purpose
Defines the abstract base for DFS referral entry encoders and decoders.

## Important APIs, Types, And Functions
Direct types: DfsReferralEntry class. Fields include none declared. Direct methods: WriteBytes, ReadEntry.

## Control Flow
`ReadEntry` peeks at the referral version in the buffer and dispatches to V1, V2, V3, or V4 constructors, while subclasses provide `WriteBytes`, `Length`, and `StringsLength`.

## State And Persistence Behavior
State is a mutable in-memory representation of one referral entry. Persistence occurs only when the entry is serialized into a DFS referral response buffer.

## Dependencies And Integration Points
Depends on little-endian helpers, UTF-16 string helpers, DFS referral enums, and `ResponseGetDfsReferral` for list assembly and parsing.

## Risks
Risks are mostly bounds and offset related: malformed buffers can point string offsets outside the packet, nullable strings are not guarded on serialization, and V3/V4 behavior depends on correctly interpreting flag combinations.

## Test Signals
Round-trip tests should cover each version, normal and name-list V3, V4 target-set-boundary flag, bad version dispatch, relative string offsets, and truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntry.cs -->
