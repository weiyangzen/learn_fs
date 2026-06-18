# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/EchoHelper.cs

## Purpose

Creates SMB1 echo responses and unsolicited echo replies used as keepalive probes.

## Important APIs, Types, And Functions

`GetEchoResponse` returns one `EchoResponse` per requested echo count, copying request data. `GetUnsolicitedEchoReply` builds a complete SMB1 message with wildcard UID/TID/PID/MID values.

## Control Flow

Normal echo loops from zero to `EchoCount - 1` and sets sequence numbers. Unsolicited echo constructs header flags compatible with NT LANMAN behavior and adds one response command.

## State And Persistence Behavior

No persisted state; keepalive sending updates connection last-send elsewhere.

## Dependencies And Integration Points

Uses SMB1 message/header/echo types. Called by command dispatch and `ConnectionManager.SendSMBKeepAlive`.

## Risks And Edge Cases

Large `EchoCount` can generate many response commands. Unsolicited replies rely on clients discarding unknown PID/MID responses as specified.

## Test Signals

Test sequence numbers, payload echoing, zero count, high count, and keepalive header values.

Source-read signal: reviewed the complete local source file for this item.
