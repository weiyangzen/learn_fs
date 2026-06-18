# sources/user-network-fs/libsmb2/include/smb2/smb2.h

## Purpose
`smb2.h` defines the public SMB2/SMB3 wire protocol constants and C structures used by the raw and high-level libsmb2 APIs.

## Important APIs, Types, and Functions
The header includes command ids, SMB2 header flags, negotiate/session/tree/create/read/write/query/set/ioctl/change-notify/oplock/lease/lock/logoff/echo constants, file access masks, attributes, share flags, create disposition/options, file and filesystem information classes, security descriptor/SID/ACE/ACL structures, reparse/symlink structures, IOCTL structs, notify structs, and request/reply structs for all major SMB2 commands. It declares helpers such as `smb2_get_file_id()`, `smb2_fh_from_file_id()`, `smb2_decode_fileidfulldirectoryinformation()`, and `smb2_decode_filenotifychangeinformation()`.

## Control Flow
There is no executable flow in the header. Runtime packers fill request structs, encode them to SMB2 wire format, receive replies, and decode bytes into reply/info structures according to the constants and fixed-size definitions here.

## State and Persistence Behavior
Most structures represent transient wire messages. Some fields refer to caller-owned or decoder-allocated buffers such as names, security descriptors, reparse data, read/write buffers, create contexts, query outputs, and notify linked lists. Remote persistence depends on commands using these structs, such as create, write, set-info, lock, and ioctl.

## Dependencies and Integration Points
It includes `smb2-errors.h` and conditionally includes `<stdint.h>`/`<time.h>` based on config macros. `libsmb2.h`, `libsmb2-raw.h`, and implementation packers/unpackers depend on this file for ABI and wire layout.

## Risks and Edge Cases
Because this is a wire-layout contract, size constants and structure fields must match SMB2 specs exactly. Duplicate macro names appear for some file information classes and oplock constants. Variable-length buffers require careful ownership and bounds checks in implementation code.

## Test Signals
Round-trip encode/decode every command struct, validate fixed-size constants against protocol examples, test security descriptor and directory info parsing, and interoperate with Windows/Samba servers for negotiate, create, read/write, query-info, ioctl, notify, oplock/lease break, and lock flows.
