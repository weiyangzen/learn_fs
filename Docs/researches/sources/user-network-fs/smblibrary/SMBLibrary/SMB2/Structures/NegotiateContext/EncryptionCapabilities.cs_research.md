# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/NegotiateContext/EncryptionCapabilities.cs

## Purpose

Implements the SMB2 encryption capabilities negotiate context, carrying the list of cipher algorithms a peer supports.

## Important APIs, Types, And Functions

Extends `NegotiateContext`, exposes `Ciphers`, overrides `WriteData`, `DataLength`, and `ContextType`.

## Control Flow

Writing emits a cipher count at data offset 0, followed by each 16-bit cipher at offset `2 + index * 2`. Reading gets the count and appends parsed enum values.

## State And Persistence Behavior

The context is transient negotiate data. Its chosen cipher affects later SMB3 transform encryption state.

## Dependencies And Integration Points

Depends on `NegotiateContext`, `CipherAlgorithm`, and `Utilities`; used by SMB2 negotiate parsing and generation.

## Risks And Edge Cases

The read loop currently reads ciphers from `Data` at `index * 2`, so the first parsed cipher is the cipher count rather than the first cipher value. This can corrupt capability negotiation. Bounds checks are also absent for short data.

## Test Signals

Parse a buffer with two known ciphers and assert the first value is not the count. Round-trip write/read and short-data failure tests should cover this file.

Source-read signal: reviewed the complete local source file for this item.
