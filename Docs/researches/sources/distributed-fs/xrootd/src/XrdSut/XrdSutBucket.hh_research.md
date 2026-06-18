# sources/distributed-fs/xrootd/src/XrdSut/XrdSutBucket.hh

## Purpose

This header declares `XrdSutBucket`, the typed byte-buffer object used as the atomic field inside XrdSut serialized authentication messages.

## Important APIs, types, and functions

Public data members are `type`, `size`, and `buffer`. Constructors support raw buffers, `XrdOucString`, and copy construction. Methods include `Update`, `SetBuf`, `Dump`, `ToString`, and equality/inequality operators. Private `membuf` tracks owned allocation.

## Control flow

The class is intentionally simple and leaves most validation to callers. Consumers create buckets, add them to `XrdSutBuffer`, and serialize/parse based on `type`.

## State and persistence behavior

No direct persistence. Bucket bytes are serialized by `XrdSutBuffer::Serialized` and may eventually be written into credentials or protocol messages. Destructor deletes `membuf`.

## Dependencies and integration points

It includes `XrdSutAux.hh` for bucket type constants and forward-declares `XrdOucString`. It is consumed by `XrdSutBuckList` and security protocol parsers.

## Risks and edge cases

Public mutable fields make it easy to break ownership or size invariants. The raw-buffer constructor takes ownership, so stack/static buffers must not be passed. There is no move/copy assignment definition.

## Test signals

Compile coverage should include consumers that manipulate public fields and use all constructors. Runtime tests belong with the implementation and buffer serialization.
