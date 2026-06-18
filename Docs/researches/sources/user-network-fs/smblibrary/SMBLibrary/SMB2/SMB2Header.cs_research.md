# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2Header.cs

## Purpose

Defines the fixed 64-byte SMB2 packet header serializer/parser used by SMB2 request and response packets. It models protocol id, command, credit fields, status, flags, chaining offset, message id, sync tree id or async id, session id, and optional signing signature.

## Important APIs, Types, And Functions

`SMB2Header(SMB2CommandName)` builds an outbound header, `SMB2Header(byte[], int)` parses inbound bytes, `WriteBytes` serializes fields, `IsResponse`, `IsAsync`, `IsRelatedOperations`, and `IsSigned` toggle flag bits, and `IsValidSMB2Header` checks the `0xFE 'SMB'` signature.

## Control Flow

Parsing reads the common prefix, then branches on `SMB2PacketHeaderFlags.AsyncCommand` to interpret bytes 32-39 as either `AsyncID` or `Reserved` plus `TreeID`. Serialization mirrors that branch and only writes the 16-byte signature when the signed flag is set.

## State And Persistence Behavior

The class is transient wire state. Persistence is limited to values copied into packet objects and later used by server dispatch, signing, compounding, and response correlation.

## Dependencies And Integration Points

Depends on `Utilities` byte readers/writers, SMB2 enums, and `NTStatus`. It integrates with packet framing, SMB2 signing, async completion, tree/session lookup, and compound `NextCommand` handling.

## Risks And Edge Cases

Parsed unsigned headers leave `Signature` unset, so downstream code must not assume a non-null array. The parser does not validate `StructureSize`, buffer length beyond the first four bytes in `IsValidSMB2Header`, or impossible flag combinations.

## Test Signals

Useful signals are round-trip byte equality for sync and async headers, signed versus unsigned signature behavior, response flag toggling, compound `NextCommand` preservation, and rejection of short or wrong-signature buffers.

Source-read signal: reviewed the complete local source file for this item.
