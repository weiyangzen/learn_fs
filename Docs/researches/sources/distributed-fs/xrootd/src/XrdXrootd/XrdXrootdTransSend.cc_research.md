# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransSend.cc

## Purpose

This file adapts bridged file responses into an `XrdLink::sfVec` sendfile operation. It lets bridge result callbacks send protocol headers/trailers plus one or more file regions.

## Important APIs, types, and functions

`XrdXrootdTransSend::Send(const iovec *headP, int headN, const iovec *tailP, int tailN)` builds a dynamic `sfVec` array from optional header iovecs, the stored file region(s), and optional trailer iovecs, then calls `linkP->Send(sfVec, numV)`.

## Control flow

For a single file descriptor, the method inserts one file segment with `sfOff`, `sfLen`, and `sfFD`. For an existing `XrdOucSFVec`, it copies file entries starting at index 1 because index 0 is reserved for a protocol header in normal response code. It deletes the temporary vector after the send.

## State and persistence behavior

The object stores borrowed file-vector or fd information from construction. It performs no persistence and does not own the underlying file descriptors.

## Dependencies and integration points

It depends on `XrdLink` and `XrdXrootdTransSend.hh`. It is created by `XrdXrootdTransit::Send()` when the protocol response uses sendfile.

## Risks and edge cases

The allocation size for vector-backed sends uses `numV - sfFD` while the send call passes `numV`; because `sfFD` is negative `sfvnum`, this allocates extra space but sends only `headN + tailN + 1` entries, potentially omitting copied file-vector entries if `sfvnum` is greater than one. This should be reviewed with actual `sfVec` expectations. Borrowed file descriptors must remain valid during the send.

## Test signals

Tests should cover single-fd sendfile, multi-vector sendfile, header/trailer inclusion, correct vector count passed to `XrdLink::Send`, and failure propagation.
