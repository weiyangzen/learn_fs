# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdReqID.hh

## Purpose

`XrdXrootdReqID` packs the information needed to route an asynchronous response back to the correct link and stream. It overlays a 64-bit id with link instance, link id/file descriptor, and two-byte stream id fields.

## Important APIs, types, and functions

`getID()` returns the packed 64-bit value. The overload `getID(unsigned char *sid, int &lid, unsigned int &linst)` decodes fields. `setID()` overloads set the packed id, set decoded fields, or update only the stream id. `Stream()` returns a pointer to the stored stream bytes.

## Control flow

Request handlers store the current stream id in `ReqID`. Async callback paths later decode the id, map the link id/instance through `XrdLinkCtl`, and send an attention/asynchronous response to the original client or bridge.

## State and persistence behavior

The state is a single union value in memory. It is not portable durable data; field layout depends on the local ABI and is used only within the process.

## Dependencies and integration points

It depends on `cstring` for `memcpy` and is included by `XrdXrootdProtocol`, `XrdXrootdResponse`, job/callback code, and async response logic.

## Risks and edge cases

The constructor `XrdXrootdReqID(const unsigned char *sid, ...)` appears to pass a null pointer to `setID()` when `sid` is non-null and `"\0\0"` when it is null, which is suspicious and should be verified against compiler warnings/tests. The union layout assumes the same endian/packing for encode and decode inside one process.

## Test signals

Tests should round-trip stream id, link id, and instance values; validate packed-id preservation; exercise default construction before use; and specifically cover the pointer conditional in the stream/link constructor.
