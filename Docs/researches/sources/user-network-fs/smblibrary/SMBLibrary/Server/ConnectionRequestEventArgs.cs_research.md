# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionRequestEventArgs.cs

## Purpose

Event argument object for server connection admission decisions.

## Important APIs, Types, And Functions

Public fields are `IPEndPoint` and `Accept`, defaulting to true. The constructor records the remote endpoint.

## Control Flow

No internal control flow; event subscribers can flip `Accept` before the server proceeds.

## State And Persistence Behavior

Per-event transient state only.

## Dependencies And Integration Points

Uses `System.Net.IPEndPoint` and `EventArgs`; integrates with connection accept hooks in the server.

## Risks And Edge Cases

Public mutable fields make validation a caller responsibility. A null endpoint is not rejected here.

## Test Signals

Test default accept behavior and server rejection path when an event handler sets `Accept = false`.

Source-read signal: reviewed the complete local source file for this item.
