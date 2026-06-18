# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/FileID.cs

## Purpose

Models the SMB2 16-byte file identifier made of persistent and volatile 64-bit ids.

## Important APIs, Types, And Functions

`FileID(byte[], int)` parses two little-endian `ulong` values and `WriteBytes` serializes them. `Length` is the fixed 16-byte wire size.

## Control Flow

No branching: persistent id is at offset 0 and volatile id at offset 8.

## State And Persistence Behavior

In this server, `SMB2Session` uses the volatile id as the dictionary key for open files and open searches; persistent is set equal to volatile because durable handles are not supported.

## Dependencies And Integration Points

Used by SMB2 create/close/read/write/query and async context code.

## Risks And Edge Cases

Durable-handle semantics are not implemented despite the persistent field. Callers must validate session scope and not trust a `FileID` from another session.

## Test Signals

Round-trip id serialization, session lookup by volatile id, invalid id rejection, and durable-handle non-support behavior are key signals.

Source-read signal: reviewed the complete local source file for this item.
