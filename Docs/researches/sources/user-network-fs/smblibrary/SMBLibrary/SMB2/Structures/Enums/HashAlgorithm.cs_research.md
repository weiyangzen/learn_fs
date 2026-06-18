# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/Enums/HashAlgorithm.cs

## Purpose

Declares the SMB 3.1.1 preauthentication integrity hash algorithm enum.

## Important APIs, Types, And Functions

`HashAlgorithm : ushort` currently exposes `SHA512 = 1`, matching SMB2 preauth integrity capabilities.

## Control Flow

No control flow; the value is serialized by preauth capability contexts.

## State And Persistence Behavior

No local state. Negotiation code uses the selected hash to build and update the preauth integrity hash.

## Dependencies And Integration Points

Used by `PreAuthIntegrityCapabilities` and SMB 3.1.1 negotiate handling.

## Risks And Edge Cases

Only SHA-512 is represented. Future algorithms would need enum and selection updates.

## Test Signals

Round-trip preauth capability parsing and negotiation should assert value `1` maps to SHA-512.

Source-read signal: reviewed the complete local source file for this item.
