# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdResponse.cc

## Purpose

This file serializes xroot server responses. It supports ordinary OK/error/data responses, redirect/status responses, sendfile payloads, bridged `XrdXrootdTransit` callbacks, and delayed asynchronous attention responses.

## Important APIs, types, and functions

`Send()` overloads build `ServerResponseHeader` plus optional data, iovec, error code, info integer, file descriptor, sendfile vector, or `ServerResponseStatus`. The static `Send(XrdXrootdReqID&, XResponseType, iovec*, ...)` sends async attention responses. `Set()` stores stream id and trace string. `srsComplete()` fills status response bodies and computes CRC32C.

## Control flow

Every send path first traces the outgoing response, prepares network byte order fields, and either calls the active bridge or writes to `XrdLink`. For sendfile, the header is inserted as the first vector and file regions follow. Static async send decodes `ReqID` to a live link, references it, checks link instance, and sends either a bridged attention response through `XrdXrootdTransit::Attn()` or a direct `kXR_attn/kXR_asynresp` envelope.

## State and persistence behavior

`XrdXrootdResponse` stores the current link, optional transit bridge, reusable header, iovec scratch array, and trace stream id. It does not persist data; it only formats outbound wire messages.

## Dependencies and integration points

The file depends on `XrdLink`, `XrdLinkCtl`, CRC utilities, protocol wire structs, tracing, request ids, and `XrdXrootdTransit`. It is used by protocol handlers, jobs, callbacks, async I/O, stats, and transit bridge code.

## Risks and edge cases

All length/status fields must be converted correctly to network byte order. Several bridge branches pass `dlen` or `ioLen` values to callbacks, so mismatched iovec length accounting can corrupt client-visible payload boundaries. Static async sends must handle stale file descriptors or recycled link instances safely; instance checking is critical.

## Test signals

Tests should cover OK/error/redirect/iovec/status/sendfile serialization, bridge-vs-direct behavior, CRC32C in status responses, async response routing to direct and bridged links, stale link instance rejection, and stream-id trace formatting.
