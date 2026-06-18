# sources/user-network-fs/samba/source3/include/MacExtensions.h

## Purpose
`MacExtensions.h` defines legacy Macintosh CIFS/AFP extension constants, stream names, AFP info structures, and Trans2 information levels used for Finder metadata, comments, desktop database calls, unique IDs, and HFS-style information over SMB.

## Important APIs, Types, And Functions
- Stream names include `.streams`, `:AFP_AfpInfo:$DATA`, `:AFP_Resource:$DATA`, `:Comments:$DATA`, desktop, and ID index streams.
- `AfpInfo` represents the NT AFP_AfpInfo stream layout with signature, version, backup time, Finder info, ProDOS info, and reserved bytes.
- `SambaAfpInfo` extends `AfpInfo` with a create time.
- `SMB_MAC_QUERY_FS_INFO`, `SMB_MAC_FIND_BOTH_HFS_INFO`, `SMB_MAC_SET_FINDER_INFO`, and desktop database info levels occupy the 0x301-0x309 range.
- Support flags describe access control, comments, desktop DB calls, unique IDs, and no-streams/no-Mac support.
- Enums define Macintosh access bits and `SMB_MAC_SET_FINDER_INFO` field masks.

## Control Flow
This is a declarative protocol header. SMB server/client Trans2 handlers use these constants to encode or decode Mac-specific requests and responses.

## State And Persistence
The header describes persistent metadata streams and database-style desktop/icon data that other modules may store. It does not implement storage itself. Structure sizes and offsets are wire/storage contracts.

## Dependencies And Integration Points
It depends on fixed-width integer types from Samba includes. It integrates with SMB Trans2 query/set path and find operations, alternate data stream handling, and AFP/OS X interoperability code.

## Risks
Wire layout constants cannot change without breaking interoperability. Comments note little-endian fields, so implementations must explicitly marshal rather than rely on host layout. The `SambaAfpInfo` use of `unsigned long` is potentially ABI-width-sensitive if serialized directly.

## Test Signals
Protocol tests should verify exact info levels, support flags, AFP info size/offsets, stream names, Finder info masks, and behavior against clients expecting Mac CIFS extensions.
