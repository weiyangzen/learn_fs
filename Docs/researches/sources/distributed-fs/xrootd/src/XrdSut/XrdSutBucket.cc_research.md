# sources/distributed-fs/xrootd/src/XrdSut/XrdSutBucket.cc

## Purpose

This file implements `XrdSutBucket`, the unit of typed binary information exchanged inside XrdSut authentication buffers. Buckets carry a type id, byte size, and buffer pointer, with optional ownership through an internal `membuf`.

## Important APIs, types, and functions

Constructors accept a raw buffer, an `XrdOucString`, or another bucket. `Update(char *, int, int)` takes ownership of a raw buffer. `Update(XrdOucString &, int)` and `SetBuf` allocate and copy. `ToString` copies bucket bytes into a null-terminated `XrdOucString`. `Dump` prints hex and printable content. `operator==` compares byte contents only.

## Control flow

String constructors and update methods allocate exactly `s.length()` bytes and copy raw string bytes without appending null terminators. `Dump` walks each byte, appends hex tokens, classifies printable ASCII with a static mask, and prints eight-byte rows.

## State and persistence behavior

State is in-memory only. Ownership is split: `buffer` points to current content and `membuf` records the buffer to delete in the destructor. Raw-buffer construction sets both pointers to the incoming pointer, so the bucket owns and deletes that buffer.

## Dependencies and integration points

The file depends on `XrdOucString`, `XrdSutAux` bucket names, and XrdSut trace macros. It is used by `XrdSutBuffer` and security protocols to carry credentials, crypto material, status values, and nested buffers.

## Risks and edge cases

The copy constructor does not initialize fields if allocation fails, leaving members potentially undefined. `operator==` ignores type and compares only size/content, which may be intentional but can surprise callers. `SetBuf` and `Update(XrdOucString)` return `-1` for empty input after clearing the bucket, so an empty bucket cannot be represented as a successful update. `Dump` assumes `buffer` is valid when `size > 0`.

## Test signals

Tests should cover ownership transfer, copy construction, update/clear behavior, equality across same bytes with different types, string conversion for binary data containing nulls, and dump output stability for printable and non-printable data.
