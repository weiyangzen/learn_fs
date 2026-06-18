# sources/distributed-fs/xrootd/src/XrdCl/XrdClMessage.hh

## Purpose

This header defines `XrdCl::Message`, the buffer-derived request/response container used throughout XrdCl for protocol messages plus metadata that is not part of the raw wire bytes.

## Important APIs, Types, And Functions

`Message` inherits `Buffer` and adds marshalled state, session ID, human-readable description, obfuscated description, and virtual request ID. Important methods are constructors, move assignment, `IsMarshalled`, `SetIsMarshalled`, `SetDescription`, `GetDescription`, `GetObfuscatedDescription`, `SetSessionId`, `GetSessionId`, `SetVirtReqID`, and `GetVirtReqID`.

## Control Flow

Message construction optionally allocates and zeroes the underlying buffer. Transport code marshals/unmarshals the raw buffer and flips `pIsMarshalled`. Higher layers set descriptions for logging and set virtual request IDs to distinguish synthetic operations such as virtual readv.

## State And Persistence

All state is in memory. Moving a message transfers the buffer and copies/moves metadata. `SetDescription` also stores `pObfuscatedDescription` by calling `obfuscateAuth`, preventing authorization parameters from leaking into logs.

## Dependencies And Integration Points

It depends on `XrdClBuffer.hh`, `XrdOucUtils.hh`, and `XrdOucPrivateUtils.hh`. It is consumed by `MessageUtils`, transports, message handlers, local file routing, redirectors, and logging.

## Risks

The move constructor does not clear the moved-from metadata, so moved-from objects should not be reused except destructively. `pIsMarshalled` must stay accurate; parsing code such as metalink CGI extraction branches on it. Descriptions are not automatically tied to buffer mutations except where callers update them, so stale descriptions are possible.

## Test Signals

Tests should cover construction with zeroing, move construction/assignment, description obfuscation for auth CGI parameters, session ID propagation, virtual request ID propagation, and marshalled flag use across transport round trips.
