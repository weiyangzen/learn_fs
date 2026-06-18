# sources/user-network-fs/samba/source3/lib/readdir_attr.h

## Purpose
This header defines extra filesystem metadata that can be carried during readdir/marshalling contexts. It currently supports no attributes or Apple-specific attributes.

## Important APIs, Types, And Functions
`enum readdir_attr_type` has `RDATTR_NONE` and `RDATTR_AAPL`. `struct readdir_attr_data` stores the active type and a union with an `aapl` payload containing resource fork size, 16 bytes of Finder info, maximum access, and Unix mode.

## Control Flow
The header has no functions or control flow. Consumers switch on `type` and read the corresponding union member.

## State And Persistence
The structure is transient per directory entry or marshalling operation. It does not own heap memory and does not persist data.

## Dependencies And Integration Points
It relies on standard fixed-width integer types and `mode_t` already made visible by included Samba/system headers. It integrates with SMB directory enumeration paths that need AAPL extension metadata.

## Risks And Test Signals
Risks are uninitialized union contents and consumers reading `aapl` fields without checking `type`. Tests should cover directory enumeration with no attributes and AAPL metadata enabled, including stable struct initialization.
