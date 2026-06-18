# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/NegotiateContext/NegotiateContext.cs

## Purpose

Provides the base SMB2 negotiate context record and list helpers for SMB 3.1.1 negotiate extensions.

## Important APIs, Types, And Functions

The base stores context type, reserved value, and raw `Data`. `ReadNegotiateContext` dispatches known types to `PreAuthIntegrityCapabilities` or `EncryptionCapabilities`; list helpers read/write 8-byte aligned context arrays and compute lengths.

## Control Flow

Reading one context consumes the fixed 8-byte header and raw data. Reading a list advances by each context's padded length. Writing calls virtual `WriteData`, writes type/length/reserved, and copies data.

## State And Persistence Behavior

No persisted state; instances carry negotiate-time metadata that later determines preauth hashing and encryption settings.

## Dependencies And Integration Points

Uses `Utilities` and negotiate context subclasses. It is consumed by negotiate request/response structures.

## Risks And Edge Cases

Unknown contexts are preserved only as raw data. The reader trusts `count`, offsets, and `DataLength`, so malformed packets can cause out-of-range reads. Padding bytes are not explicitly zeroed by this class.

## Test Signals

Test dispatch for known types, raw preservation for unknown types, padded list offsets, last-entry unpadded length computation, and short-buffer rejection at the packet layer.

Source-read signal: reviewed the complete local source file for this item.
