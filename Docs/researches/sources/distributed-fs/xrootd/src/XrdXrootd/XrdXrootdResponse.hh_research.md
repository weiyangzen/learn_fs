# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdResponse.hh

## Purpose

This header declares the response writer used by xroot protocol handlers. It abstracts the difference between writing to a client `XrdLink` and returning results through a transit bridge.

## Important APIs, types, and functions

The class exposes overloads for success, message, error, raw data, iovec data, typed response data, redirects/info responses, sendfile, status responses, and static async response sends. `Set()` binds either an `XrdLink`, an `XrdXrootdTransit`, or a stream id. `isOurs()` distinguishes direct-link responses from bridged ones.

## Control flow

Protocol handlers set the stream id from the current request, then call the appropriate `Send()` overload. The implementation fills `Resp` and writes through the link or bridge. Static send is used by job/callback code that only has a packed `ReqID`.

## State and persistence behavior

The class owns no payload memory. It keeps a reusable header and small iovec array, borrowing caller data during send. It has no durable state.

## Dependencies and integration points

It depends on wire protocol types, `XrdXrootdReqID`, `XrdLink`, `XrdXrootdTransit`, and `XrdOucSFVec`. It is embedded in `XrdXrootdProtocol` and used across job, callback, async, stats, and bridge paths.

## Risks and edge cases

Borrowed buffers must remain valid for the duration of synchronous `Link->Send()`. Copy/assignment copy link, bridge, and stream id but not any ownership, so response objects are lightweight handles. Sendfile methods assume sendfile enablement has already been checked by callers.

## Test signals

Compile and behavioral tests should verify overload selection, bridge/direct path switching, stream-id preservation after copy/assignment, and async static send integration.
