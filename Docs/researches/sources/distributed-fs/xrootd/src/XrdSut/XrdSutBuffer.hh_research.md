# sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuffer.hh

## Purpose

This header declares `XrdSutBuffer`, the typed bucket container used to build and parse XRootD security handshake messages.

## Important APIs, types, and functions

Constructors create an outbound buffer from protocol/options or parse serialized bytes. Inline `AddBucket` overloads add raw buffers, strings, or existing bucket pointers. Other APIs update, remove, dump, serialize, deactivate, marshal/unmarshal integer buckets, find buckets by type/tag, inspect bucket count/protocol/options/step, and increment the step.

## Control flow

Consumers build messages by adding buckets and serializing, or parse incoming bytes then query buckets by type. The step number tracks handshake iteration.

## State and persistence behavior

The class owns its buckets and stores protocol/options/step in memory. Serialized output is caller-owned and can be transmitted or stored elsewhere.

## Dependencies and integration points

It includes `XrdSutBuckList.hh` and forward-declares `XrdOucString`. It is part of the security utility target and a core dependency of password/GSI security protocols.

## Risks and edge cases

The inline `AddBucket(char *bp, ...)` constructs a bucket that owns `bp`; callers must not reuse or free that memory. `GetBuckList` casts away constness. The API exposes raw bucket pointers and removal is only from the list, not deletion, so ownership transfer must be explicit.

## Test signals

Header/API tests should exercise all add overloads, removal without deletion, step mutation, and source compatibility for protocol consumers.
