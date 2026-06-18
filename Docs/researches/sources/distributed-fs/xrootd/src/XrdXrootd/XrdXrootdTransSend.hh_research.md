# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransSend.hh

## Purpose

This header declares `XrdXrootdTransSend`, a `Bridge::Context` subclass that carries sendfile metadata for bridged file responses.

## Important APIs, types, and functions

Two constructors capture either a single `fdnum/offset/dlen` or an `XrdOucSFVec` array plus count and length. `Send()` is the bridge callback method that writes headers, file regions, and trailers to the underlying link.

## Control flow

`XrdXrootdTransit` constructs this context when a protocol handler emits sendfile output through a bridge. The bridge result object calls `Send()` to actually transfer file bytes.

## State and persistence behavior

State is transient and borrows the link and file metadata. The union stores either an offset or a pointer to the original sendfile vector; `sfFD` is positive for single fd and negative for vector count.

## Dependencies and integration points

It depends on `XrdXrootdBridge.hh`, `XPtypes.hh`, and `sys/uio.h`, plus forward-declared `XrdLink`. It integrates with transit bridge file callbacks.

## Risks and edge cases

The sign-overloaded `sfFD` is compact but easy to misuse. The vector constructor borrows `sfvec`; callers must ensure it remains valid until `Send()` completes.

## Test signals

Tests should verify constructor mode selection, context stream/request metadata, and send behavior for both single and vector file paths.
