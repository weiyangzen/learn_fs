# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB2ConnectionState.cs

## Purpose

Extends base connection state with SMB2 sessions and async request tracking.

## Important APIs, Types, And Functions

Methods allocate/create/get/remove sessions, close all sessions, collect session information, allocate async ids, and create/get/remove async contexts.

## Control Flow

Session ids and async ids scan from monotonic counters, skip reserved values, then add to dictionaries. Session removal closes the session before removing it. Async contexts are keyed by generated async id.

## State And Persistence Behavior

Connection-local dictionaries for sessions and pending SMB2 operations. Persistent file state is held by session open-file handles and underlying file stores.

## Dependencies And Integration Points

Depends on `SMB2Session`, `SMB2AsyncContext`, `FileID`, and base `ConnectionState`.

## Risks And Edge Cases

Dictionary membership checks in allocation are not locked consistently with dictionary mutation. The code skips `0xFFFFFFFF` but not all protocol-reserved 64-bit ids. Durable/persistent reconnect state is not represented.

## Test Signals

Test session allocation/removal, async allocation wraparound, session info aggregation, close cleanup, and races between async completion and session removal.

Source-read signal: reviewed the complete local source file for this item.
