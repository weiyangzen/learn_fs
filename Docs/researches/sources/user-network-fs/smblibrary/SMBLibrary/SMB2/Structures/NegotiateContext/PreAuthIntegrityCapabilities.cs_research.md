# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/NegotiateContext/PreAuthIntegrityCapabilities.cs

## Purpose

Implements the SMB2 preauthentication integrity capabilities negotiate context, including supported hash algorithms and salt.

## Important APIs, Types, And Functions

Extends `NegotiateContext`, exposes `HashAlgorithms` and `Salt`, overrides `WriteData`, `DataLength`, and `ContextType`.

## Control Flow

Parsing reads hash count and salt length, reads each 16-bit hash algorithm starting at offset 4, then reads salt after the algorithm list. Writing emits the same layout.

## State And Persistence Behavior

The context is negotiate-time data. The selected algorithm and salt feed SMB 3.1.1 preauth integrity computation outside this file.

## Dependencies And Integration Points

Depends on `HashAlgorithm`, `NegotiateContext`, and byte utilities.

## Risks And Edge Cases

`Salt` is not initialized by the default constructor, so callers must set it before `DataLength` or `WriteData`. The parser trusts lengths without data-size validation.

## Test Signals

Round-trip tests should cover one SHA-512 value, non-empty salt, empty salt if allowed, null-salt guard behavior, and malformed short data.

Source-read signal: reviewed the complete local source file for this item.
