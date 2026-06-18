# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB1ConnectionState.cs

## Purpose

Extends `ConnectionState` with SMB1-specific session, tree id, file id, transaction assembly, and async request tracking.

## Important APIs, Types, And Functions

Provides allocation and CRUD methods for UIDs, sessions, TIDs, FIDs, process states, and async contexts. Overrides session cleanup and session information aggregation.

## Control Flow

Allocation scans from the next id, skips reserved values, and checks all relevant dictionaries. Session removal closes resources before deleting. Async contexts are searched by UID/TID/PID/MID.

## State And Persistence Behavior

All state is connection-local memory: sessions by UID, process state by PID, and pending async list. Closing sessions closes open files through session close paths.

## Dependencies And Integration Points

Depends on `SMB1Session`, `ProcessStateObject`, `SMB1AsyncContext`, and base connection state.

## Risks And Edge Cases

Some scans over sessions are not protected by `m_sessions` locks even though sessions can mutate. PID-only process state can collide for concurrent transactions. Reserved-value handling skips zero TID/FID despite comments saying zero is valid.

## Test Signals

Test allocation wraparound and reserved values, concurrent session add/remove, transaction state lifecycle, async lookup/removal, and close-session file cleanup.

Source-read signal: reviewed the complete local source file for this item.
