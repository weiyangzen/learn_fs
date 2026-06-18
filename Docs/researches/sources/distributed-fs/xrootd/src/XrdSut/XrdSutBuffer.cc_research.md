# sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuffer.cc

## Purpose

This file implements `XrdSutBuffer`, the bucketized wire/message container used by XrdSec password and GSI protocols. It can parse an initial `&P=<protocol>,<options>` buffer or a serialized exchange buffer containing protocol id, step number, and typed buckets.

## Important APIs, types, and functions

Important methods are the buffer-parsing constructor, destructor, `UpdateBucket`, `Dump`, `Message`, `MarshalBucket`, `UnmarshalBucket`, `GetBucket`, `Deactivate`, and `Serialized`. The header also provides inline `AddBucket`, `Remove`, accessors, and step mutators.

## Control flow

Parsing first distinguishes `&P=` initial negotiation buffers from full exchange buffers. Full parsing reads a null-terminated protocol id, a network-order step, then repeats `type`, `length`, `data` until `kXRS_none`, skipping inactive buckets. Serialization performs the inverse: protocol string, network-order step, active buckets only, and a `kXRS_none` terminator. `MarshalBucket` stores a 32-bit integer in network byte order and `UnmarshalBucket` validates size before converting back.

## State and persistence behavior

The object owns buckets in `fBuckets` and deletes them in the destructor. It stores protocol name, options, and step as transient message state. Serialized bytes may be transmitted or nested in other buckets; no direct disk persistence occurs here.

## Dependencies and integration points

The file depends on XRootD security protocol id size, network byte-order helpers, `XrdOucString`, `XrdSutBucket`, `XrdSutBuckList`, and XrdSut tracing. It is heavily used by `XrdSecpwd` and `XrdSecgsi` handshake parsing and construction.

## Risks and edge cases

The parser has limited bounds validation. It reads `type` and `blen` before ensuring enough bytes remain for those fields, and the total-length calculation excludes only the step size, not the protocol prefix, so malformed inputs deserve careful fuzzing. Serialization copies `bp->buffer` for any active bucket regardless of null when size is nonzero. The destructor deletes buckets while iterating a list that does not own bucket nodes, relying on the list cursor remaining valid. `Serialized` allocation ownership depends on `opt` (`new[]` vs `malloc`), which callers must match.

## Test signals

Tests should cover initial negotiation parsing, full serialize/parse round trips, inactive bucket omission, integer marshal/unmarshal with wrong size, tagged bucket lookup, malformed/truncated buffers, zero-size buckets, nested buffers, and caller cleanup for both allocation modes.
