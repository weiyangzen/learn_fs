# sources/user-network-fs/smblibrary/SMBLibrary/Server/Enums/SMBDialect.cs

## Purpose

Defines the server's coarse negotiated SMB dialect enum.

## Important APIs, Types, And Functions

Values are `NotSet`, `NTLM012`, `SMB202`, `SMB210`, and `SMB300`.

## Control Flow

No control flow; connection negotiation stores one value in `ConnectionState.Dialect`.

## State And Persistence Behavior

Connection-level negotiated protocol state.

## Dependencies And Integration Points

Used by connection/session information and dialect-specific dispatch.

## Risks And Edge Cases

The enum stops at SMB 3.0 while other source files include SMB 3.1.1 structures; reporting or gating may be too coarse for newer dialect behavior.

## Test Signals

Negotiation tests should assert expected enum values and session information reporting for SMB1 and SMB2 connections.

Source-read signal: reviewed the complete local source file for this item.
