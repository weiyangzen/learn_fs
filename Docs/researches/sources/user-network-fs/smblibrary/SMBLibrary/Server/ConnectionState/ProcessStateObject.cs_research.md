# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/ProcessStateObject.cs

## Purpose

Holds partial SMB1 transaction or NT transaction request state while secondary packets arrive.

## Important APIs, Types, And Functions

Public fields capture subcommand id, max response sizes, timeout, transaction name, setup bytes, full parameter/data buffers, and received byte counts.

## Control Flow

Transaction helpers create one object by PID, copy initial fragments, then secondary requests write into the buffers by displacement until both received counts reach total lengths.

## State And Persistence Behavior

Connection-scoped in-memory assembly state keyed by process id in `SMB1ConnectionState`.

## Dependencies And Integration Points

Used by `TransactionHelper` and `NTTransactHelper`.

## Risks And Edge Cases

State is keyed only by PID, so overlapping transactions from the same PID can collide. Received counts are incremented by fragment length rather than tracking unique ranges, so duplicate or overlapping secondary packets can make a transaction appear complete incorrectly.

## Test Signals

Test multi-fragment assembly, out-of-order displacement, duplicate fragment handling, PID collision behavior, and cleanup after complete or invalid sequences.

Source-read signal: reviewed the complete local source file for this item.
