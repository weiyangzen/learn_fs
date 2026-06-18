# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/CreateContext.cs

## Purpose

Represents an SMB2 `SMB2_CREATE_CONTEXT` entry and static helpers for reading, writing, and sizing lists of create contexts attached to SMB2 CREATE requests and responses.

## Important APIs, Types, And Functions

Fields include `Next`, `Name`, `Data`, and reserved/offset bookkeeping. The constructor parses one context, private `WriteBytes` serializes one context, `Length` sizes it, and the list helpers process 8-byte aligned chains.

## Control Flow

Reading follows each context's `Next` offset until zero. Writing computes each context length, pads all but the last to 8-byte alignment, stores `Next`, then writes name and data payload at computed offsets.

## State And Persistence Behavior

The structure carries create-time extension state such as durable handles, leases, query-on-disk-id, or negotiate contexts. It is not persisted by itself; server/client create handlers interpret `Name` and `Data`.

## Dependencies And Integration Points

Uses `Utilities` byte helpers and `Math.Ceiling`. It integrates with SMB2 CREATE marshalling and context-specific parsers outside this file.

## Risks And Edge Cases

`WriteBytes` treats `Name` as ANSI bytes, but `Length` multiplies `Name.Length` by two; this can overestimate buffers and offsets relative to actual write behavior. The reader trusts offsets and lengths without bounds checks or cycle protection on malformed `Next` chains.

## Test Signals

Test one and multiple contexts, empty data, non-8-byte name lengths, exact `Next` offsets, malformed offsets, and create-context names with non-ASCII characters if the protocol layer claims ANSI semantics.

Source-read signal: reviewed the complete local source file for this item.
